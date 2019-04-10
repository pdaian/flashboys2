from web3 import Web3
import csv, csv_hack, time
from receipts import write_receipt

my_provider = Web3.IPCProvider('/home/geth/parity_mainnet/jsonrpc.ipc', timeout=60)
w3 = Web3(my_provider)

bidder_txs = []

print("Preprocessing phase 1 done!")

bidsdict = csv.DictReader(open('data/all_success_arb_txs_bigquery.csv'))
for bid in bidsdict:
    bidder_txs.append(bid['transaction_hash'])

print("Preprocessing phase 2 done!")

bidsdict = csv.DictReader(open('data/arb_receipts.csv'))
for bid in bidsdict:
    bidder_txs.remove(bid['hash'])

print("Preprocessing done!")

f = open('data/arb_receipts.csv', 'a')
#f.write("block_num,tx_position,gas_limit,gas_price,gas_used,from,to,input,hash,log_addrs,log_topics,log_data,gastoken\n")

i = 0
curr_time = time.time()

for txhash in bidder_txs:
    print(txhash)
    receipt = w3.eth.getTransactionReceipt(txhash)
    tx = w3.eth.getTransaction(txhash)
    i += 1
    if (i % 10) == 0:
        print(i, "processed", time.time() - curr_time)
        curr_time = time.time()
    if receipt is None:
        continue
    write_receipt(receipt, tx, f)
