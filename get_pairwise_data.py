import csv, csv_hack, json
from receipts import write_receipt

auctions = {}

bidsdict = csv.DictReader(open('data/auctions.csv'))
for bid in bidsdict:
    auction_num = bid['auction_id']
    if not auction_num in auctions:
        auctions[auction_num] = []
    auctions[auction_num].append(bid)

self_price_deltas = {}
pairwise_price_deltas = {}
pairwise_price_percent_deltas = {}
self_price_percent_deltas = {}
self_time_deltas = {}
pairwise_time_deltas = {}

pairs = {}
auctions_participated = {}

for auction_num in auctions:
    last_bid = None
    last_bids_by_id = {}
    for bid in auctions[auction_num]:
        sender = bid['sender']
        if not sender in auctions_participated:
            auctions_participated[sender] = set()
        auctions_participated[sender].add(auction_num)
        bid['gas_price'] = int(bid['gas_price'])
        bid['time_seen'] = int(bid['time_seen'])
        if last_bid is not None:
            counterbidder = last_bid['sender']
            price_delta = bid['gas_price'] - last_bid['gas_price']
            price_percent_delta = (price_delta / (float(bid['gas_price'] + last_bid['gas_price'])/2)) * 100
            time_delta = (bid['time_seen'] - last_bid['time_seen']) / (10 ** 9)
            price_delta /=(10 ** 9)
            if price_delta < 0:
                continue # ignore bids that aren't raises; TODO check effects
            bidder_pairs = str(sender) + "-" + str(counterbidder)
            if not bidder_pairs in pairwise_price_deltas:
                pairwise_price_deltas[bidder_pairs] = []
                pairwise_price_percent_deltas[bidder_pairs] = []
                pairwise_time_deltas[bidder_pairs] = []
                pairs[sender] = set()
            pairwise_time_deltas[bidder_pairs].append(time_delta)
            pairwise_price_deltas[bidder_pairs].append(price_delta)
            pairwise_price_percent_deltas[bidder_pairs].append(price_percent_delta)
            pairs[sender].add(bidder_pairs)

        if sender in last_bids_by_id:
            last_self_bid = last_bids_by_id[sender]
            price_delta = bid['gas_price'] - last_self_bid['gas_price']
            time_delta = (bid['time_seen'] - last_self_bid['time_seen']) / (10 ** 9)
            price_percent_delta = (price_delta / ((bid['gas_price'] + last_self_bid['gas_price'])/2)) * 100
            price_delta /=(10 ** 9)
            if not sender in self_price_deltas:
                self_time_deltas[sender] = []
                self_price_deltas[sender] = []
                self_price_percent_deltas[sender] = []
            self_time_deltas[sender].append(time_delta)
            self_price_deltas[sender].append(price_delta)
            self_price_percent_deltas[sender].append(price_percent_delta)
        last_bid = bid
        last_bids_by_id[sender] = bid

# convert sets to lists for json reasons
for pair in pairs:
    pairs[pair] = list(pairs[pair])

for sender in auctions_participated:
    auctions_participated[sender] = list(auctions_participated[sender])

print(pairs)

data = {"pairwise_time": pairwise_time_deltas, "pairwise_price": pairwise_price_deltas,"pairwise_price_percent": pairwise_price_percent_deltas,"self_time": self_time_deltas,"self_price": self_price_deltas, "self_price_percent": self_price_deltas, "pairs": pairs, "auctions": auctions_participated}
f = open('data/pairwise_self.csv', 'w')
f.write(json.dumps(data))

