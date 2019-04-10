import csv

all_txs = set() # set of all tx ids seen as hashes
earliest_seen = {} # hash to earliest line (orderdict) observed of this instance
all_seen = {} # hash to each line (ordereddict) observed of this instance
hits = {} # hash to number of times seen total by all monitors

num_processed = 0
CUTOFF = 10000000000000000000000
#CUTOFF = 1000000

def print_seen_line(seen_item, prev_seen_item, display_payload):
    print("%.6f" % ((seen_item['time_seen'] - prev_seen_item['time_seen'])/10**9), "%.6f" % (seen_item['time_seen'] / (10 ** 9)), seen_item['hash'], seen_item['sender'], seen_item['account_nonce'], seen_item['gas_price'], "H:" + str(hits[seen_item['hash']]), seen_item['payload'] if display_payload else "", sep="\t")

def print_seen_dict(seen_tuple_dictionary):
    for monitor_ip in seen_tuple_dictionary:
        monitor_seen = seen_tuple_dictionary[monitor_ip]
        print_seen_list(monitor_seen)
        print("-" * 50, "\n")

def print_seen_list(seen_list, display_payload=True, print_first_item=True):
    if print_first_item:
        # first line doesn't have a prev item
        print_seen_line(seen_list[0], seen_list[0], display_payload)

    for i in range(len(seen_list) - 1):
        prev_item = seen_list[i]
        item = seen_list[i+1]
        print_seen_line(item, prev_item, display_payload)
        #open(monitor_ip, "a").write(item['hash'] + "\n")

def get_bidder(item):
    return (item['sender'], item['account_nonce'])

def add_bidder_to(auction_participation, bidder, auction_id):
    if bidder in auction_participation:
        if auction_id in auction_participation[bidder]:
            auction_participation[bidder][auction_id] += 1
        else:
            auction_participation[bidder][auction_id] = 1
    else:
        auction_participation[bidder] = {auction_id: 1}

def should_filter_frontier(frontier, bidder_id):
    bid_addr = bidder_id[0]
    bid_nonce = int(bidder_id[1])
    if bid_addr in frontier:
        if frontier[bid_addr] > bid_nonce + 2: # (choose magic number 2 as threshold for out-of-ordering TODO repair)
            return True
        frontier[bid_addr] = max(frontier[bid_addr], bid_nonce)
    else:
        frontier[bid_addr] = bid_nonce
    return False

def prefilter_list(seen_list):
    allowed_addrs = open("filter_list.txt").read().strip().splitlines()
    frontier = {} # maps address bidding to latest known nonce
    filtered_list = []
    for item in seen_list:
        bidder_id = get_bidder(item)
        print(item)
        #if int(item['gas_price']) < 20000000000 or int(item['gas_limit']) < 100000: # was <= 80
        #if int(item['gas_price']) < 2000 or int(item['gas_limit']) < 100000: # was <= 80
        #    continue
        if should_filter_frontier(frontier, bidder_id):
            continue
        #if not item['sender'].lower() in allowed_addrs:
        #    continue
        filtered_list.append(item)
    return filtered_list


def get_individual_auctions(seen_list):
    # IMPORTANT: ASSUMES DEDUPING (see map to line below)
    auctions = [] # list of seen lists for output auctions.  each transaction represents a "bid"
    auction_bidders = [] # list of set of bidders [bidder is a tuple of (hash, nonce)] in each of the above auctions, indexed similarly
    non_auction_txs = []
    # garbage_txs = [] # transactions that were a product of syncing (behind the frontier) TODO populate

    auction_participation = {} # maps bidders to maps of (auction_id : tuple(str,str) to num_bid : int)

    curr_auction = []
    curr_bidders = set()
    auction_id = 0
    for i in range(len(seen_list) - 1):
        prev_item = seen_list[i]
        item = seen_list[i+1]
        time_difference = (item['time_seen'] - prev_item['time_seen'])/10**9

        if time_difference < 3:
            # this tx is part of the auction
            bidder_id = get_bidder(item)
            if len(curr_auction) == 0:
                # new auction; previous tx must have triggered
                curr_auction = [prev_item, item]
                # previous tx actually isn't non-auction
                non_auction_txs = non_auction_txs[:-1]
                original_bidder_id = get_bidder(prev_item)
                curr_bidders.add(original_bidder_id)
                curr_bidders.add(bidder_id)
                add_bidder_to(auction_participation, original_bidder_id, auction_id)
            else:
                curr_auction.append(item)
                curr_bidders.add(bidder_id)
            add_bidder_to(auction_participation, bidder_id, auction_id)
        else:
            # tx is not part of an auction
            if len(curr_auction) != 0:
                # some previous auction ended; log and reset
                auctions.append(curr_auction)
                auction_bidders += [curr_bidders]
                curr_auction = []
                curr_bidders = set()
                auction_id += 1
            non_auction_txs.append(item)

    if len(curr_auction) != 0:
        # last straggler auction
        auctions.append(curr_auction)
        auction_bidders += [curr_bidders]
    return auctions, non_auction_txs, auction_bidders, auction_participation

with open('arbitrage_data.csv', 'r' ) as f:
    reader = csv.DictReader(f)
    for line in reader:
        if line['time_seen'] == 'time_seen':
            # duplicate header line, ignore (happens when combining datasets)
            continue

        if line['gas_price'] == '':
            # [NOTE this prunes all gas-empty bids]
            continue

        # line preprocessing (eg type conversions)
        line['time_seen'] = int(line['time_seen'])
        line['gas_price'] = int(line['gas_price'])
        hash = line['hash']

        all_txs.add(hash)
        if hash in earliest_seen:
            if earliest_seen[hash]['time_seen'] > line['time_seen']:
                earliest_seen[hash] = line
            #all_seen[hash].append(line)
            hits[hash] += 1
        else:
            #all_seen[hash] = [line]
            earliest_seen[hash] = line
            hits[hash] = 1
        num_processed += 1
        if num_processed > CUTOFF:
            break

seen_times = {} # monitor ip to list of (time_seen, tx_data) for all txs seen
global_seen = [] # list of (time_first_ever_seen, tx_data) for all txs seen

# comments - disable all_seen for resource reasons (TODO refactor)
#for hash in all_seen:
for hash in earliest_seen:
#    for line in all_seen[hash]:
     #for line in earliest_seen[hash]:
        #monitor_ip = line['monitor_ip']
        #if not monitor_ip in seen_times:
        #    seen_times[monitor_ip] = []
        #seen_times[monitor_ip].append(line)
     global_seen.append(earliest_seen[hash])


print("DONE2")
# sort seen_times and global_seen
for monitor_ip in seen_times:
    seen_times[monitor_ip] = sorted(seen_times[monitor_ip], key=lambda line: line['time_seen'])

global_seen = sorted(global_seen, key=lambda line: line['time_seen'])

print("UNFILTERED GLOBAL LIST")
print_seen_list(global_seen,display_payload=False)
global_seen = prefilter_list(global_seen)

print("FILTERED GLOBAL LIST")
print_seen_list(global_seen,display_payload=False)
auctions, non_auctions, bidders, participation = get_individual_auctions(global_seen)

def postprocess_bid_list(all_bids):
    last_bid = None
    last_bids_by_id = {}
    for bid in all_bids:
        # insert blanks for first bids, etc
        bid['price_delta'] = ''
        bid['price_percent_delta'] = ''
        bid['time_delta'] = ''
        bid['self_price_delta'] = ''
        bid['self_price_percent_delta'] = ''
        bid['self_time_delta'] = ''
        sender = bid['sender']
        if last_bid is not None:
            price_delta = bid['gas_price'] - last_bid['gas_price']
            try:
                price_percent_delta = (price_delta / (float(bid['gas_price'] + last_bid['gas_price'])/2)) * 100
            except:
                price_percent_delta = 0.0
            try:
                time_delta = (bid['time_seen'] - last_bid['time_seen']) / (10 ** 9)
            except:
                # todo when do these division-by-0 cases happen (this and above)?
                time_delta = 0.0
            price_delta /=(10 ** 9)
            bid['price_delta'] = price_delta
            bid['price_percent_delta'] = price_percent_delta
            bid['time_delta'] = time_delta

        if sender in last_bids_by_id:
            last_self_bid = last_bids_by_id[sender]
            price_delta = bid['gas_price'] - last_self_bid['gas_price']
            time_delta = (bid['time_seen'] - last_self_bid['time_seen']) / (10 ** 9)
            try:
                price_percent_delta = (price_delta / (last_self_bid['gas_price'])) * 100
            except:
                price_percent_delta = 0.0
            price_delta /=(10 ** 9)
            bid['self_price_delta'] = price_delta
            bid['self_price_percent_delta'] = price_percent_delta
            bid['self_time_delta'] = time_delta
        last_bid = bid
        last_bids_by_id[sender] = bid

    return all_bids

def normalize_auction_ids(participation, auction_list):
    auctionspans = []
    bids_per_auction = {}
    for bidder in participation:
        bidder_auctions = participation[bidder]
        if sum(bidder_auctions.values()) == 1:
            continue
            # not a repeated bid; ignore

        # keep track of total repeated bids in each auction ID; heaviest ID is the canonical auction
        for auction_id in bidder_auctions:
            if not auction_id in bids_per_auction:
                bids_per_auction[auction_id] = 0
            bids_per_auction[auction_id] += bidder_auctions[auction_id]

        auctionspan = max(bidder_auctions.keys()) - min(bidder_auctions.keys())
        auctionspans.append(auctionspan)
        print(bidder, bidder_auctions, auctionspan)

    # show delta statistics
    for i in range(max(auctionspans)):
        print(i, auctionspans.count(i))

    # populate canonical auction list with repeated bidders in each of those auctions
    canonical_bidders = {} # maps canonical auction ids to list of bidders
    for bidder in participation:
        bidder_auctions = participation[bidder]
        if sum(bidder_auctions.values()) == 1:
            continue
            # not a repeated bid; ignore

        auctionspan = max(bidder_auctions.keys()) - min(bidder_auctions.keys())
        if auctionspan > 1:
            # data quality issues; todo check manually and validate constants
            continue

        canonical_auction = -1
        best_bids = -1
        for auction_id in bidder_auctions:
            auction_bids = bids_per_auction[auction_id]
            canonical_auction = canonical_auction if auction_bids < best_bids else auction_id
            best_bids = bids_per_auction[canonical_auction]
        if not canonical_auction in canonical_bidders:
            canonical_bidders[canonical_auction] = []
        canonical_bidders[canonical_auction].append(bidder)

    print("CANONICAL LIST")
    for auction_id in canonical_bidders:
        print(auction_id, canonical_bidders[auction_id], len(canonical_bidders[auction_id]))


    normalized_auction_list = []
    for canonical_auction_id in range(0, max(canonical_bidders.keys())):
        if canonical_auction_id in canonical_bidders:
            if len(canonical_bidders[canonical_auction_id]) < 2:
                continue # todo check these
            auction_bidders = canonical_bidders[canonical_auction_id]
            # add all bids out-of-period by accounts that rebid here
            all_bids = []
            auctions_bid_in = set([canonical_auction_id])
            for bidder in auction_bidders:
                for auction in participation[bidder]:
                    auctions_bid_in.add(auction)
            auctions_bid_in = sorted(list(auctions_bid_in))
            for auction in auctions_bid_in:
                if auction == canonical_auction_id:
                    all_bids += auction_list[auction] # add all in-period bids
                else:
                    for bid in auction_list[auction]:
                        if bid['sender'] == bidder[0] and bid['account_nonce'] == bidder[1]:
                            all_bids.append(bid)
            max_gas_price = max([int(x['gas_price']) for x in all_bids])
            min_gas_price = min([int(x['gas_price']) for x in all_bids])
            if max_gas_price - min_gas_price >= 100000000000:
                all_bids = postprocess_bid_list(all_bids)
                normalized_auction_list.append(all_bids)

    for auction in normalized_auction_list:
        print("NORMD AUCTION:")
        print_seen_list(auction, display_payload=False)
        print("\n\n")

    return normalized_auction_list

for bidder_group in bidders:
    print(bidder_group)
    print("\n\n")

for auction in auctions:
    print("AUCTION:")
    print_seen_list(auction, display_payload=False)
    print("\n\n")

print("NON-AUCTION")
print_seen_list(auction, display_payload=False)


normalized_auctions = normalize_auction_ids(participation, auctions)

def write_normalized_list(normalized_auctions, output_file):
    f = open(output_file, 'w')
    w = csv.DictWriter(f, ["auction_id"] + list(normalized_auctions[0][0].keys()))
    w.writeheader()
    for auction_id in range(len(normalized_auctions)):
        auction = normalized_auctions[auction_id]
        for bid in auction:
            bid["auction_id"] = auction_id
        w.writerows(auction)
    f.close()

write_normalized_list(normalized_auctions, "data/auctions.csv")

exit(1)

unique_seen_times = {} # duplicate seens removed, structure as seen_times

for monitor_ip in seen_times:
    txs_seen_by_monitor = set()
    unique_seen_times[monitor_ip] = []
    monitor_seen = seen_times[monitor_ip]
    for item in monitor_seen:
        hash = item['hash']
        if hash not in txs_seen_by_monitor and hits[hash] > 4:
            unique_seen_times[monitor_ip].append(item)
            txs_seen_by_monitor.add(hash)

#unique_seen_times = {'35.200.170.118': unique_seen_times['35.200.170.118']}

print_seen_dict(unique_seen_times)
