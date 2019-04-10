import pygraphviz as pgv
import csv, csv_hack, os
import json
from exchanges import get_trade_data_from_log_item

COLORS = ["red", "blue", "green", "orange", "purple", "black", "yellow", "grey", "darkgreen"] * 10

logsdict = csv.DictReader(open('data/all_logs_bigquery.csv'), delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
logs = {}

def get_rate_label(token1, amount1, token2, amount2):
    if (token1 >= token2 and token1 != "ETH" and token1 != "WETH") or (token2 == "ETH" or token2 == "WETH"): # arbitrary ordering/ tiebreak
        try:
            return "%4g %s" % (amount1/amount2, token1 + '/' + token2)
        except ZeroDivisionError:
            return "[INF] %s" % (token1 + '/' + token2)
    try:
        return "%4g %s" % (amount2/amount1, token2 + '/' + token1)
    except ZeroDivisionError:
        return "[INF] %s" % (token2 + '/' + token1)


def get_profit_graph(logset, txhash):
    dot = pgv.AGraph(label=txhash + ' Profit Flow', directed=True, strict=False, nodesep=1.0, ranksep=0.5, sep=0.0, labelfloat=False)
    unknown = False
    graph_edges = []
    logindex = 1
    tokens_involved = set()
    trades = []
    for logitem in logset:
        address = logitem[0]
        data = logitem[1]
        topicstext = logitem[2].replace('\'', '\"')
        topics = json.loads(topicstext)
        data = data[2:] # strip 0x from hex
        trades_data = get_trade_data_from_log_item(topics, data, address)
        if trades_data is not None:
            for trade_data in trades_data:
                (tokenget_addr, tokenget_label, tokenget, amountget, tokengive_addr, tokengive_label, tokengive, amountgive, exchange) = trade_data
                graph_edges.append((tokenget, "!" + exchange, amountget)) # (add "!" to mark special exchange node)
                graph_edges.append(("!" + exchange, tokengive, amountgive))

                rate_label = get_rate_label(tokenget, amountget, tokengive, amountgive)
                tradenode_label = "Trade #" + str(logindex) + " (" + exchange + ")\n" + rate_label
                dot.add_edge(tokenget_label, tradenode_label, label=("%4g" % amountget), color=COLORS[logindex])
                dot.add_edge(tradenode_label, tokengive_label, label=("%4g" % amountgive), color=COLORS[logindex])
                trades.append(tradenode_label)
                tokens_involved.add(tokenget_label)
                tokens_involved.add(tokengive_label)
                logindex += 1
        else:
            # some item in the logset failed to parse => we don't have complete profit picture
            unknown = True
    for token in list(tokens_involved):
        dot.add_subgraph(token, rank='same')
    dot.add_subgraph(trades, rank='same')
    for i in range(0, len(trades) - 1):
        dot.add_edge(trades[i], trades[i+1], style="invis")
    return(graph_edges, unknown, dot)

def calculate_profit_for(profit_graph):
    token_profits = {}
    for edge in profit_graph:
        if not edge[0] in token_profits:
            token_profits[edge[0]] = 0
        if not edge[1] in token_profits:
            token_profits[edge[1]] = 0
        token_profits[edge[0]] -= edge[2]
        token_profits[edge[1]] += edge[2]
    return token_profits

for log in logsdict:
    hash = log['transaction_hash']
    if not hash in logs:
        logs[hash] = []
    logs[hash].append((log['address'], log['data'], log['topics']))


spamwriter = csv.writer(open('data/profits.csv', 'w'), delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
spamwriter.writerow(["txhash","drawn","unknown","all_positive","eth_profit","profit_graph","profit_calcs"])

i = 0
total = len(logs)
for txhash in logs:
    i += 1
    print(txhash, i, "of", total)
    output_file_name = 'profit_graphs/' + txhash + '.png'
    drawn = False
    (profit_graph, unknown, dot) = get_profit_graph(logs[txhash], txhash)
    if unknown:
        # failed to process given entry because some exchange that's in dex_list.py is missing a log parser
        print("UNKNOWN!", txhash)
    if not unknown and len(profit_graph) > 2:
        if not os.path.exists(output_file_name):
            dot.draw(output_file_name, prog="dot")
        drawn = True
    profit_calcs = calculate_profit_for(profit_graph)
    all_positive = True
    for token in profit_calcs:
        if token[0] != "!":
            if profit_calcs[token] < 0:
                all_positive = False
    profit_graph_data = json.dumps(profit_graph)
    profit_calcs_data = json.dumps(profit_calcs)
    spamwriter.writerow([txhash, drawn, unknown, all_positive, profit_calcs.get('ETH', 0), profit_graph_data, profit_calcs_data])
