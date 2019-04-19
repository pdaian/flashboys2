from flask import Flask
import sqlite3
import ipaddress
from flask import current_app, g, render_template, request, jsonify
import datetime
from flask_basicauth import BasicAuth
import string

app = Flask(__name__)

app.config['BASIC_AUTH_USERNAME'] = 'bro'
app.config['BASIC_AUTH_PASSWORD'] = 'passwordsaresupersecurewhenuploadedtogithub'
app.config['BASIC_AUTH_FORCE'] = True

basic_auth = BasicAuth(app)

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            'nodestatus.db',
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.executescript(
        """
            CREATE TABLE IF NOT EXISTS nodestatus (
              ipaddress TEXT UNIQUE NOT NULL,
              myhostname TEXT NOT NULL,
              timelastchecked TEXT NOT NULL,
              syncing INTEGER NOT NULL,
              currentBlock INTEGER,
              highestBlock INTEGER,
              knownStates INTEGER,
              pulledStates INTEGER,
              startingBlock INTEGER,
              timesYesSynced INTEGER,
              timesNotSynced INTEGER
            );
            CREATE TABLE IF NOT EXISTS monitorlist (
              ethaddress TEXT UNIQUE NOT NULL
            );
        """
    )

@app.route('/', methods=['GET'])
def display_index():
    init_db()
    cur = get_db().cursor()
    cur.execute('SELECT myhostname, ipaddress, timelastchecked, syncing, currentblock, highestblock, knownstates, pulledstates, startingblock, timesYesSynced, timesNotSynced FROM nodestatus')
    infolist = cur.fetchall()
    outlist = []
    for statusRow in infolist:
        if len(statusRow) != 0:
            statusRow = list(statusRow)
            timesYesSynced = int(statusRow[-2])
            timesNotSynced = int(statusRow[-1])
            percentUp = (float(timesYesSynced) / (float(timesYesSynced) + float(timesNotSynced))) * 100
            newStatusRow = statusRow[:-2]
            newStatusRow.append(percentUp)
            outlist.append(newStatusRow)
        else:
            return render_template('index.html', infolist=[])

    return render_template('index.html', infolist=outlist)


@app.route('/lolstatusinsertlol', methods=['POST'])
def insert_row():
    nodeAddress = request.form.get('ipaddress')
    try:
        nadr = ipaddress.ip_address(nodeAddress)
        nodeAddress = str(nadr)
    except ValueError:
        return "error not a valid IP yo", 400
    myhostname = str(request.form.get('myhostname'))
    timelastchecked = datetime.datetime.fromtimestamp(int(request.form.get('timelastchecked'))).strftime("%Y-%m-%d %H:%M:%S %Z") if request.form.get('timelastchecked') else ""
    syncing = str(request.form.get('syncing')) if request.form.get('syncing') else ""
    currentBlock = int(request.form.get('currentBlock')) if request.form.get('currentBlock') else ""
    highestBlock = int(request.form.get('highestBlock')) if request.form.get('highestBlock') else ""
    knownStates = int(request.form.get('knownStates')) if request.form.get('knownStates') else ""
    pulledStates = int(request.form.get('pulledStates')) if request.form.get('pulledStates') else ""
    startingBlock = int(request.form.get('startingBlock')) if request.form.get('startingBlock') else ""
    init_db()
    cur = get_db().cursor()
    cur.execute('SELECT timesYesSynced, timesNotSynced FROM nodestatus WHERE myhostname == ?', (myhostname,))
    ilist = cur.fetchall()
    if len(ilist) != 0:
        reslist = ilist[0]
        if len(reslist) == 2:
            timesYesSynced = int(reslist[0])
            timesNotSynced = int(reslist[1])
        else:
            timesYesSynced = 0
            timesNotSynced = 0
    else:
        timesYesSynced = 0
        timesNotSynced = 0

    if syncing.lower() == "true":
        timesNotSynced += 1
    elif syncing.lower() == "false":
        timesYesSynced += 1
    else:
        return "ERR somehow the sync status came in as not true or false", 500

    inserttuple = (
        nodeAddress,
        myhostname,
        timelastchecked,
        syncing,
        currentBlock,
        highestBlock,
        knownStates,
        pulledStates,
        startingBlock,
        timesYesSynced,
        timesNotSynced
    )
    cur.execute('INSERT OR REPLACE INTO nodestatus VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', inserttuple)
    get_db().commit()
    return 'ok', 200


@app.route('/lolgetsomeaddresses', methods=['POST'])
def retrieve_monitor_list():
    clientversion = int(request.form.get('version'))
    # insert into versiontable values(1);
    # sqlite> create table versiontable("version" int unique not null);
    # sqlite> select version from versiontable;
    # sqlite> insert into versiontable values(1);
    # sqlite> select version from versiontable;
    # 1
    init_db()
    cur = get_db().cursor()

    cur.execute('SELECT version FROM versiontable')
    infolist = cur.fetchall()
    serverversion = int(infolist[0][0])

    if clientversion != serverversion:
        cur.execute('SELECT ethaddress FROM monitorlist')
        infolist = cur.fetchall()
        outlist = []
        for row in infolist:
            outlist.append(str(row[0]))
        return jsonify(Listy=outlist, ListVersion=serverversion)
    else:
        return jsonify(Listy=[], ListVersion=serverversion)

@app.route('/manageaddresslist', methods=['GET'])
def display_manage_monitor_list():
    init_db()
    cur = get_db().cursor()
    cur.execute('SELECT ethaddress FROM monitorlist')
    infolist = cur.fetchall()
    outlist = []
    for row in infolist:
        outlist.append(str(row[0]))
    return render_template('insertpage.html', outlist=outlist)

def is_hex(s):
     hex_digits = set(string.hexdigits)
     # if s is long, then it is faster to check against a set
     return all(c in hex_digits for c in s)

@app.route('/lolpostsomeaddressses', methods=['POST'])
def update_monitor_list():
    updateListBlob = request.form.get('updateList')
    if updateListBlob:
        init_db()
        cur = get_db().cursor()
        errs = []

        cur.execute('SELECT version FROM versiontable')
        infolist = cur.fetchall()
        serverversion = int(infolist[0][0])

        for lineToProcess in updateListBlob.split("\n"):
            lineToProcess = lineToProcess.lstrip().rstrip().lower()
            if len(lineToProcess) == 42 and lineToProcess[0:2] == "0x" and is_hex(lineToProcess[2:]):
                cur.execute('INSERT OR IGNORE INTO monitorlist VALUES (?)', (lineToProcess, ))
            else:
                errs.append(lineToProcess)

        cur.execute('UPDATE versiontable SET version=? WHERE version=?;', ((serverversion + 1), serverversion))

        get_db().commit()
        if len(errs) != 0:
            return "errors occured!!! list of lines that were wrong {}".format(str(errs)), 200
        return updateListBlob, 200
    return "error, updateList is empty", 400

if __name__ == '__main__':
    app.run()
