import csv, csv_hack, sys

infile = sys.argv[1]
outfile = sys.argv[2]

def init_zero_dict(dict, val):
    if not val in dict:
        dict[val] = 0

total_gwei_bid = {}
total_gwei_used = {}
total_gas_bid = {}
total_gas_used = {}

BINWIDTH = 10000
num_txs = 0

bidsdict = csv.DictReader(open(infile))
for bid in bidsdict:
    if len(bid['input']) < 8:
        continue
    num_txs += 1
    blocknum = int(bid['block_number'])
    price_bid = int(bid['gas_price'])
    gas_bid = int(bid['gas'])
    gas_used = int(bid['receipt_gas_used'])
    init_zero_dict(total_gwei_bid, blocknum)
    init_zero_dict(total_gwei_used, blocknum)
    init_zero_dict(total_gas_bid, blocknum)
    init_zero_dict(total_gas_used, blocknum)
    total_gwei_bid[blocknum] += (price_bid * float(gas_bid)) / (10 ** 9)
    total_gwei_used[blocknum] += (price_bid * float(gas_used)) / (10 ** 9)
    total_gas_bid[blocknum] += gas_bid
    total_gas_used[blocknum] += gas_used

print("Block range", min(total_gwei_bid.keys()), max(total_gwei_bid.keys()))
print("Num txs", num_txs)
print("Total gwei bid", sum(total_gwei_bid.values()))
print("Total gwei used", sum(total_gwei_used.values()))
print("Total gas bid", sum(total_gas_bid.values()))

blockstats = [0, 0]
data = []
for blocknum in range(min(total_gwei_bid.keys()), max(total_gwei_bid.keys()) + 1, BINWIDTH):
    start = blocknum
    end = min(blocknum + BINWIDTH, max(total_gwei_bid.keys()) + 1)
    total_gwei_bid_range = 0
    total_gwei_used_range = 0
    total_gas_bid_range = 0
    total_gas_used_range = 0
    for i in range(start, end):
        if i in total_gwei_bid:
            blockstats[0] += 1
            total_gwei_bid_range += total_gwei_bid[i]
            total_gwei_used_range += total_gwei_used[i]
            total_gas_bid_range += total_gas_bid[i]
            total_gas_used_range += total_gas_used[i]
        else:
            blockstats[1] += 1

    data.append([start, end, total_gwei_bid_range, total_gwei_used_range, total_gas_bid_range, total_gas_used_range])

print("Yes/no", blockstats)

open(outfile, 'w').write(str(data))


