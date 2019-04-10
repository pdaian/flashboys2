from gastoken import is_using_gastoken
import binascii

def hex2str(hex):
    return "0x" + binascii.hexlify(hex).decode("utf-8")

def write_receipt(receipt, tx, loghandle):
    addrs = "~".join([log['address'] for log in receipt['logs']])
    topics = "~".join(["|".join([hex2str(x) for x in log['topics']]) for log in receipt['logs']])
    data = "~".join([log['data'] for log in receipt['logs']])
    gas_used = receipt['gasUsed']
    txhash = hex2str(tx['hash'])
    gastoken = -1
    #if gas_used < (0.6 * tx['gas']):
    #    gastoken = is_using_gastoken(txhash)
    gastoken = -200 # TODO fix this check
    loghandle.write(str(receipt['blockNumber']) + ","  + str(receipt['transactionIndex']) + "," + str(tx['gas']) + "," + str(tx['gasPrice']) + "," + str(gas_used) + "," + str(tx['from']) + ","+ str(tx['to']) + ","+ str(tx['input']) + ","+ txhash + "," + addrs + "," + topics + "," + data + "," + str(gastoken) + "\n")

