import psycopg2, time, csv, os

def get_last_line():
    with open('arbitrage_data.csv', 'rb') as f:
        f.seek(-2, os.SEEK_END)
        while f.read(1) != b'\n':
            f.seek(-2, os.SEEK_CUR) 
        return str(int(f.readline().decode().split(",")[-1])) # make sure it parses as int implicitly (or typeerror)


FIELDS_TO_GRAB = 'hash,monitor_ip,sender,time_seen,payload,gas_price,gas_limit,amount,peer_name,account_nonce,id'

conn = psycopg2.connect("postgres://tkell:d8HqKH;2~>~=@arbitrage3.ck0rrdngnqmh.us-west-2.rds.amazonaws.com/arbitrage?sslmode=verify-full")
cur = conn.cursor()
print(time.time())

grab_from = get_last_line()
print("[database fetcher] Grabbing starting at id " + grab_from)
cur.execute("SELECT " + FIELDS_TO_GRAB + " FROM arbitrage WHERE id > " + get_last_line() +  " ;")
print(time.time())

with open('arbitrage_data.csv', 'a') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)

    #spamwriter.writerow(FIELDS_TO_GRAB.split(","))
    for item in cur.fetchall():
        spamwriter.writerow(item)

print("[database fetcher] Wrote to id " + get_last_line())
