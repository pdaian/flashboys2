import argparse
from _pysha3 import keccak_256
from web3 import Web3, HTTPProvider
import json

web3 = Web3(HTTPProvider('http://localhost:8549'))
#web3 = Web3(HTTPProvider('https://mainnet.infura.io/Ky03pelFIxoZdAUsr82w'))

etherDeltaAddress = '0x8d12A197cB00D4747a1fe03395095ce2A5CC6819'
etherAddress = '0000000000000000000000000000000000000000000000000000000000000000'

tradeAPI = '0x' + \
           keccak_256(
               b'Trade(address,uint256,address,uint256,address,address)'
           ).hexdigest()

parser = argparse.ArgumentParser(description='EtherDelta Arbitrage Bot.')
parser.add_argument('--st',dest='st' ,type=int, action='store', default='5000000')
parser.add_argument('--len',dest='len' ,type=int, action='store', default='100')
parser.add_argument('--r',dest='r' ,type=int, action='store', default='20')
args = parser.parse_args()

startBlock = args.st
endBlock = args.st + args.len
ratio = args.r
result_dir = '../results/succ_txs-{}-{}-{}.txt'.format(startBlock,endBlock,ratio)


import os
if os.path.isfile(result_dir):
    print('Previous file exists.')
    with open(result_dir, 'r') as f:
        lines = f.readlines()
        if(len(lines) >= 1):
            print('last line:',lines[-1])
            number = int(lines[-1].split()[0])

else:
    print('No previous file.')
    number = 0



for idx in range(max(startBlock, number), endBlock + 1, ratio):
        block = web3.eth.getBlock(idx)
        transactions = block['transactions']
        print('block number:', idx)
        for txHash in transactions:
            tx = web3.eth.getTransaction(txHash)
            receipt = web3.eth.getTransactionReceipt(txHash)
            token_pair_list = []
            for log in receipt['logs']:
                if 'topics' in log and len(log['topics']):
                    if log['topics'][0].hex() == tradeAPI:
                      token_pair_list.append((log['data'][24 + 2: 64 + 2],log['data'][24 + 128 + 2: 64 + 128+ 2]))

            num = len(token_pair_list)
            tag = None
            if num == 2 and token_pair_list[0][0] == token_pair_list[1][1] and token_pair_list[1][0] == token_pair_list[0][1]:
                tag = 'Arbitrage'
            elif num == 1:
                tag = 'Trade'
            elif num:
                tag = 'Unknown'
            if tag is not None:
                result = "{} {} {} {} {} {}\n".format(idx, txHash.hex(), tag, tx['from'], tx['to'], tx['input'])
                print(result)
                with open(result_dir,'a') as f:
                    f.write(result)


