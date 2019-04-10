from web3 import Web3
import os, binascii

my_provider = Web3.IPCProvider('/home/geth/parity_mainnet/jsonrpc.ipc')
w3 = Web3(my_provider)


def is_using_gastoken(hash):
    while True:
        try:
            trace = w3.parity.traceReplayTransaction(hash,mode=["vmTrace"])
            break
        except Exception as e:
            print(e)
    zerostores = 0
    if trace['vmTrace'] is None or trace['vmTrace']['ops'] is None:
        return -1
    for op in trace['vmTrace']['ops']:
        if op['ex'] is None or op['ex']['store'] is None:
            continue
        storeop = op['ex']['store']
        if storeop is not None and storeop['val'] == '0x0':
            zerostores += 1
    return (zerostores)


