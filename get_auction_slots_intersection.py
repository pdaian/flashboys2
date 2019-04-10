from web3 import Web3
import csv, csv_hack
from receipts import write_receipt

my_provider = Web3.HTTPProvider('https://mainnet.infura.io/v3/c534d76d934f40498f6d6113a46c6ab3')
w3 = Web3(my_provider)

bidder_txs = []

highest_block_seen = -1
old_auctions = csv.DictReader(open('data/slot_auction.csv'))
for line in old_auctions:
    if int(line['block_num']) > highest_block_seen:
        highest_block_seen = int(line['block_num'])
        last_tx_seen = line['hash']

print('seen to', highest_block_seen)

bidsdict = csv.DictReader(open('data/auctions.csv'))
reached_new_txs = False
for bid in bidsdict:
    if bid['hash'] == last_tx_seen:
        reached_new_txs = True
    if reached_new_txs:
        bidder_txs.append(bid['hash'])

#bidder_txs = bidder_txs.difference(seen_hashes)
print('done')
print(len(bidder_txs))

f = open('data/slot_auction.csv', 'a')
#f.write("block_num,tx_position,gas_limit,gas_price,gas_used,from,to,input,hash,log_addrs,log_topics,log_data,gastoken\n")

for txhash in bidder_txs:
    receipt = w3.eth.getTransactionReceipt(txhash)
    tx = w3.eth.getTransaction(txhash)
    if receipt is None:
        continue

    write_receipt(receipt, tx, f)
