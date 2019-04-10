from web3 import Web3
from receipts import write_receipt

LOGOUT = "data/gas_slots_6207336_6146507.csv"

START_BLOCK = 6207336
END_BLOCK = 6146507

curr_block = START_BLOCK

my_provider = Web3.IPCProvider('/home/geth/parity_mainnet/jsonrpc.ipc')
w3 = Web3(my_provider)
loghandle = open(LOGOUT, "w")
loghandle.write("block_num,tx_position,gas_limit,gas_price,gas_used,from,to,input,hash,log_addrs,log_topics,log_data,gastoken\n")

while curr_block >= END_BLOCK:
    while True:
        try:
            block = w3.eth.getBlock(curr_block, full_transactions=True)
            break
        except:
            pass # retry in the event of an error
    numtxs = len(block['transactions'])
    for txposition in range(0, 10):
        if txposition >= numtxs:
            break
        tx = block['transactions'][txposition]
        while True:
            try:
                receipt = w3.eth.getTransactionReceipt(tx['hash'])
                break
            except Exception as e:
                print(e) # retry in the event of an error

        write_receipt(receipt, tx, loghandle)

    # now do top 10 gas price level txs
    gas_prices = {}
    for tx in block['transactions']:
        gas_price = int(tx['gasPrice'])
        if not gas_price in gas_prices:
            gas_prices[gas_price] = []
        gas_prices[gas_price].append(tx)

    sorted_prices = sorted(gas_prices.keys(), reverse=True)[:10]
    for price in sorted_prices:
        for tx in gas_prices[price]:
            while True:
                try:
                    receipt = w3.eth.getTransactionReceipt(tx['hash'])
                    break
                except Exception as e:
                    print(e) # retry in the event of an error
            write_receipt(receipt, tx, loghandle)

    print("Done with block", curr_block)
    curr_block -= 1

