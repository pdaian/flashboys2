from sqlite_adapter import *
import os, sys
import datetime, json, random
from flask import Flask, render_template, request, g, Markup
app = Flask(__name__)

DEFAULT_AUCTIONS_LIMIT = 20
DEFAULT_TXS_LIMIT = 2000


from werkzeug.contrib.cache import SimpleCache

if sys.argv[1] == "--dev":
    CACHE_TIMEOUT = -2
else:
    CACHE_TIMEOUT = 3000

cache = SimpleCache()

class cached(object):

    def __init__(self, timeout=None):
        self.timeout = timeout or CACHE_TIMEOUT

    def __call__(self, f):
        def decorator(*args, **kwargs):
            response = cache.get(request.path)
            if response is None:
                response = f(*args, **kwargs)
                cache.set(request.path, response, self.timeout)
            return response
        return decorator


def get_range(page, limit, start, end, max_val):
    limits = ((page-1)*limit, page*limit)
    if start is None:
        start = max_val - limits[0]
        end=max(max_val - limits[1], 0)
    else:
        if end is None:
            end = start
        end = end - 1
    return (start, end)


# SQLITE UTILITY FUNCTIONS - http://flask.pocoo.org/docs/0.12/patterns/sqlite3/
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def parse_profit_graph(profit_graph):
    profitstr = "<h4>Trade Log</h4><br>"
    exchanges = set()
    for trade_index in range(0, len(profit_graph), 2):
        exchange = profit_graph[trade_index][1][1:]
        profitstr += "<b>" + exchange + "</b>: "
        profitstr += str(profit_graph[trade_index][2]) + " " + profit_graph[trade_index][0] + " to " + str(profit_graph[trade_index+1][2]) + " " + profit_graph[trade_index+1][1]
        profitstr += "<br>"
    return Markup(profitstr)

def parse_profits(profit_data):
    eth_profit = profit_data.get('ETH', 0)
    profitstr = "<h4>Profits</h4><br>"
    profitstr += "<b>ETH</b>: " + str(eth_profit) + "<br>"
    for token in profit_data:
        if token != "ETH" and not "!" in token:
            profitstr += "<i>" + token + "</i>: " + str(profit_data[token]) + "<br>"
    return Markup(profitstr)

# END SQLITE UTILITY FUNCTIONS

@app.route('/global')
def global_stats():
    blockstats_wfail = open('../data/bq_inclfail_aggregate.csv').read()
    blockstats_success = open('../data/bq_success_aggregate.csv').read()
    return render_template("global.html", blockstats_wfail=blockstats_wfail, blockstats_success=blockstats_success)

@app.route('/revenuegraphs')
def revenue_graphs():
    stats = query_db("""SELECT block_number,SUM(CAST(eth_profit as INTEGER)) AS total_profit,SUM(CAST(gas as INTEGER)) AS total_gas_bid,SUM(CAST(receipt_gas_used as INTEGER)) AS total_gas_used FROM mergedprofitabletxs WHERE all_positive="True" GROUP BY block_number ORDER BY mergedprofitabletxs.rowid DESC;""")
    stats = [dict(stat) for stat in stats]
    print(stats)
    return render_template("revenuegraphs.html", stats=stats)

@app.route('/revenue/', defaults={'page': 1, 'limit': DEFAULT_TXS_LIMIT, 'start': None, 'end': None})
@app.route('/revenue/page/<int:page>', defaults={'limit': DEFAULT_TXS_LIMIT, 'start': None, 'end': None})
@app.route('/revenue/page/<int:page>/limit/<int:limit>', defaults={'start': None, 'end': None})
@app.route('/revenue/range/<int:end>/<int:start>', defaults={'page': -1, 'limit': DEFAULT_TXS_LIMIT})
def revenue(page, limit, start, end):
    max_tx = query_db('SELECT MAX(rowid) from mergedprofitabletxs', one=True)[0]
    lastpage = int(max_tx/limit) + 1
    (start_id, end_id) = get_range(lastpage - page - 1, limit, start, end, max_tx)
    txs = query_db('SELECT * FROM mergedprofitabletxs WHERE rowid > ? AND rowid <= ? AND drawn="True" ORDER BY rowid DESC', (end_id, start_id))
    profits = []
    for tx in txs:
        tx = dict(tx)
        tx['drawn'] = (tx['drawn'] == "True")
        tx['all_positive'] = (tx['all_positive'] == "True")
        tx['unknown'] = (tx['unknown'] == "True") # todo remove this field, replace w profit graph is none
        if tx['profit_graph'] != None:
            tx['profit_graph'] = json.loads(tx['profit_graph'])
            tx['profit_calcs'] = json.loads(tx['profit_calcs'])
        profits.append(tx)
    return render_template("profit.html", txs=profits, limit=limit, limits=(500, 1000, 5000), page=page, lastpage=lastpage, basepath='/revenue', graph_parser=parse_profit_graph, profit_parser=parse_profits)

@app.route('/strategies')
def strategies():
    return render_template("strategies.html", pairwise_data = json.loads(open('../data/pairwise_self.csv').read()))

@app.route('/', defaults={'page': 1, 'limit': DEFAULT_AUCTIONS_LIMIT, 'start': None, 'end': None})
@app.route('/page/<int:page>', defaults={'limit': DEFAULT_AUCTIONS_LIMIT, 'start': None, 'end': None})
@app.route('/page/<int:page>/limit/<int:limit>', defaults={'start': None, 'end': None})
@app.route('/range/<int:end>/<int:start>', defaults={'page': -1, 'limit': DEFAULT_AUCTIONS_LIMIT})
@app.route('/auction/<int:start>', defaults={'page': -1, 'limit': DEFAULT_AUCTIONS_LIMIT, 'end': None})
@cached()
def hello_world(page, limit, start, end):
    # build and process auctions
    auctions = {}
    max_auction = query_db('SELECT MAX(CAST(auction_id as decimal)) from auctions', one=True)[0]
    (start_id, end_id) = get_range(page, limit, start, end, max_auction)
    bidsdict = query_db('SELECT * FROM auctions LEFT JOIN success ON success.transaction_hash=auctions.hash WHERE auction_id >= ? AND auction_id <= ?', (end_id, start_id))
    for bid in bidsdict:
        bid = dict(bid) # convert sqlite row to dict
        if bid['transaction_hash'] != None:
            print(bid)
        auction_id = int(bid['auction_id'])
        if bid['num_logs'] != None:
            bid['num_logs'] = int(bid['num_logs'])
        bid['time_seen'] = int(bid['time_seen'])
        bid['gas_price'] = int(bid['gas_price'])
        bid['drawn'] = os.path.exists("static/profit/%s.png" % bid['hash'])
        bid['date'] = datetime.datetime.utcfromtimestamp(bid['time_seen'] / (10 ** 9))
        if auction_id in auctions:
            auctions[auction_id].append(bid)
        else:
            auctions[auction_id] = [bid]
    for auction in auctions:
        auction = auctions[auction]
        bid_times = [bid['time_seen'] for bid in auction]
        start_time = min(bid_times)
        for bid in auction:
            bid['time_delta'] = bid['time_seen'] - start_time


    # build and process slots; ugly af, sorry :(
    slots = open('../data/slots.csv').read().splitlines()
    slots = [[float(y) for y in x.split(",")] for x in slots]

    hide_global_graphs = request.args.get('hideglobal') is not None

    return render_template("index.html", auctions=auctions, max_auction=max_auction, slots=slots, start=start_id, end=end_id, limit=limit, limits=(5,10,20,50,100), page=page, lastpage=int(max_auction/limit)+1, hide_global_graphs=hide_global_graphs, deanon=("frontrun.me" in request.url))


if __name__ == "__main__":
    if sys.argv[1] == "--dev":
        app.run(host='0.0.0.0', debug=True, port=5000, threaded=True)
    else:
        app.run(host='frontrun.me', debug=False, port=80, threaded=True) # using dev servers in production booooo
