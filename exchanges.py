import json
from persistence import persist_to_file
import web3
from web3 import Web3
from eth_abi import decode_abi

ERC20_ABI = json.loads('[{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_spender","type":"address"},{"name":"_value","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_from","type":"address"},{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"_owner","type":"address"},{"name":"_spender","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"anonymous":false,"inputs":[{"indexed":true,"name":"_from","type":"address"},{"indexed":true,"name":"_to","type":"address"},{"indexed":false,"name":"_value","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"_owner","type":"address"},{"indexed":true,"name":"_spender","type":"address"},{"indexed":false,"name":"_value","type":"uint256"}],"name":"Approval","type":"event"}]')  # noqa: 501
UNISWAP_ABI = json.loads('[{"name": "TokenPurchase", "inputs": [{"type": "address", "name": "buyer", "indexed": true}, {"type": "uint256", "name": "eth_sold", "indexed": true}, {"type": "uint256", "name": "tokens_bought", "indexed": true}], "anonymous": false, "type": "event"}, {"name": "EthPurchase", "inputs": [{"type": "address", "name": "buyer", "indexed": true}, {"type": "uint256", "name": "tokens_sold", "indexed": true}, {"type": "uint256", "name": "eth_bought", "indexed": true}], "anonymous": false, "type": "event"}, {"name": "AddLiquidity", "inputs": [{"type": "address", "name": "provider", "indexed": true}, {"type": "uint256", "name": "eth_amount", "indexed": true}, {"type": "uint256", "name": "token_amount", "indexed": true}], "anonymous": false, "type": "event"}, {"name": "RemoveLiquidity", "inputs": [{"type": "address", "name": "provider", "indexed": true}, {"type": "uint256", "name": "eth_amount", "indexed": true}, {"type": "uint256", "name": "token_amount", "indexed": true}], "anonymous": false, "type": "event"}, {"name": "Transfer", "inputs": [{"type": "address", "name": "_from", "indexed": true}, {"type": "address", "name": "_to", "indexed": true}, {"type": "uint256", "name": "_value", "indexed": false}], "anonymous": false, "type": "event"}, {"name": "Approval", "inputs": [{"type": "address", "name": "_owner", "indexed": true}, {"type": "address", "name": "_spender", "indexed": true}, {"type": "uint256", "name": "_value", "indexed": false}], "anonymous": false, "type": "event"}, {"name": "setup", "outputs": [], "inputs": [{"type": "address", "name": "token_addr"}], "constant": false, "payable": false, "type": "function", "gas": 175875}, {"name": "addLiquidity", "outputs": [{"type": "uint256", "name": "out"}], "inputs": [{"type": "uint256", "name": "min_liquidity"}, {"type": "uint256", "name": "max_tokens"}, {"type": "uint256", "name": "deadline"}], "constant": false, "payable": true, "type": "function", "gas": 82616}, {"name": "removeLiquidity", "outputs": [{"type": "uint256", "name": "out"}, {"type": "uint256", "name": "out"}], "inputs": [{"type": "uint256", "name": "amount"}, {"type": "uint256", "name": "min_eth"}, {"type": "uint256", "name": "min_tokens"}, {"type": "uint256", "name": "deadline"}], "constant": false, "payable": false, "type": "function", "gas": 116814}, {"name": "__default__", "outputs": [], "inputs": [], "constant": false, "payable": true, "type": "function"}, {"name": "ethToTokenSwapInput", "outputs": [{"type": "uint256", "name": "out"}], "inputs": [{"type": "uint256", "name": "min_tokens"}, {"type": "uint256", "name": "deadline"}], "constant": false, "payable": true, "type": "function", "gas": 12757}, {"name": "ethToTokenTransferInput", "outputs": [{"type": "uint256", "name": "out"}], "inputs": [{"type": "uint256", "name": "min_tokens"}, {"type": "uint256", "name": "deadline"}, {"type": "address", "name": "recipient"}], "constant": false, "payable": true, "type": "function", "gas": 12965}, {"name": "ethToTokenSwapOutput", "outputs": [{"type": "uint256", "name": "out"}], "inputs": [{"type": "uint256", "name": "tokens_bought"}, {"type": "uint256", "name": "deadline"}], "constant": false, "payable": true, "type": "function", "gas": 50463}, {"name": "ethToTokenTransferOutput", "outputs": [{"type": "uint256", "name": "out"}], "inputs": [{"type": "uint256", "name": "tokens_bought"}, {"type": "uint256", "name": "deadline"}, {"type": "address", "name": "recipient"}], "constant": false, "payable": true, "type": "function", "gas": 50671}, {"name": "tokenToEthSwapInput", "outputs": [{"type": "uint256", "name": "out"}], "inputs": [{"type": "uint256", "name": "tokens_sold"}, {"type": "uint256", "name": "min_eth"}, {"type": "uint256", "name": "deadline"}], "constant": false, "payable": false, "type": "function", "gas": 47503}, {"name": "tokenToEthTransferInput", "outputs": [{"type": "uint256", "name": "out"}], "inputs": [{"type": "uint256", "name": "tokens_sold"}, {"type": "uint256", "name": "min_eth"}, {"type": "uint256", "name": "deadline"}, {"type": "address", "name": "recipient"}], "constant": false, "payable": false, "type": "function", "gas": 47712}, {"name": "tokenToEthSwapOutput", "outputs": [{"type": "uint256", "name": "out"}], "inputs": [{"type": "uint256", "name": "eth_bought"}, {"type": "uint256", "name": "max_tokens"}, {"type": "uint256", "name": "deadline"}], "constant": false, "payable": false, "type": "function", "gas": 50175}, {"name": "tokenToEthTransferOutput", "outputs": [{"type": "uint256", "name": "out"}], "inputs": [{"type": "uint256", "name": "eth_bought"}, {"type": "uint256", "name": "max_tokens"}, {"type": "uint256", "name": "deadline"}, {"type": "address", "name": "recipient"}], "constant": false, "payable": false, "type": "function", "gas": 50384}, {"name": "tokenToTokenSwapInput", "outputs": [{"type": "uint256", "name": "out"}], "inputs": [{"type": "uint256", "name": "tokens_sold"}, {"type": "uint256", "name": "min_tokens_bought"}, {"type": "uint256", "name": "min_eth_bought"}, {"type": "uint256", "name": "deadline"}, {"type": "address", "name": "token_addr"}], "constant": false, "payable": false, "type": "function", "gas": 51007}, {"name": "tokenToTokenTransferInput", "outputs": [{"type": "uint256", "name": "out"}], "inputs": [{"type": "uint256", "name": "tokens_sold"}, {"type": "uint256", "name": "min_tokens_bought"}, {"type": "uint256", "name": "min_eth_bought"}, {"type": "uint256", "name": "deadline"}, {"type": "address", "name": "recipient"}, {"type": "address", "name": "token_addr"}], "constant": false, "payable": false, "type": "function", "gas": 51098}, {"name": "tokenToTokenSwapOutput", "outputs": [{"type": "uint256", "name": "out"}], "inputs": [{"type": "uint256", "name": "tokens_bought"}, {"type": "uint256", "name": "max_tokens_sold"}, {"type": "uint256", "name": "max_eth_sold"}, {"type": "uint256", "name": "deadline"}, {"type": "address", "name": "token_addr"}], "constant": false, "payable": false, "type": "function", "gas": 54928}, {"name": "tokenToTokenTransferOutput", "outputs": [{"type": "uint256", "name": "out"}], "inputs": [{"type": "uint256", "name": "tokens_bought"}, {"type": "uint256", "name": "max_tokens_sold"}, {"type": "uint256", "name": "max_eth_sold"}, {"type": "uint256", "name": "deadline"}, {"type": "address", "name": "recipient"}, {"type": "address", "name": "token_addr"}], "constant": false, "payable": false, "type": "function", "gas": 55019}, {"name": "tokenToExchangeSwapInput", "outputs": [{"type": "uint256", "name": "out"}], "inputs": [{"type": "uint256", "name": "tokens_sold"}, {"type": "uint256", "name": "min_tokens_bought"}, {"type": "uint256", "name": "min_eth_bought"}, {"type": "uint256", "name": "deadline"}, {"type": "address", "name": "exchange_addr"}], "constant": false, "payable": false, "type": "function", "gas": 49342}, {"name": "tokenToExchangeTransferInput", "outputs": [{"type": "uint256", "name": "out"}], "inputs": [{"type": "uint256", "name": "tokens_sold"}, {"type": "uint256", "name": "min_tokens_bought"}, {"type": "uint256", "name": "min_eth_bought"}, {"type": "uint256", "name": "deadline"}, {"type": "address", "name": "recipient"}, {"type": "address", "name": "exchange_addr"}], "constant": false, "payable": false, "type": "function", "gas": 49532}, {"name": "tokenToExchangeSwapOutput", "outputs": [{"type": "uint256", "name": "out"}], "inputs": [{"type": "uint256", "name": "tokens_bought"}, {"type": "uint256", "name": "max_tokens_sold"}, {"type": "uint256", "name": "max_eth_sold"}, {"type": "uint256", "name": "deadline"}, {"type": "address", "name": "exchange_addr"}], "constant": false, "payable": false, "type": "function", "gas": 53233}, {"name": "tokenToExchangeTransferOutput", "outputs": [{"type": "uint256", "name": "out"}], "inputs": [{"type": "uint256", "name": "tokens_bought"}, {"type": "uint256", "name": "max_tokens_sold"}, {"type": "uint256", "name": "max_eth_sold"}, {"type": "uint256", "name": "deadline"}, {"type": "address", "name": "recipient"}, {"type": "address", "name": "exchange_addr"}], "constant": false, "payable": false, "type": "function", "gas": 53423}, {"name": "getEthToTokenInputPrice", "outputs": [{"type": "uint256", "name": "out"}], "inputs": [{"type": "uint256", "name": "eth_sold"}], "constant": true, "payable": false, "type": "function", "gas": 5542}, {"name": "getEthToTokenOutputPrice", "outputs": [{"type": "uint256", "name": "out"}], "inputs": [{"type": "uint256", "name": "tokens_bought"}], "constant": true, "payable": false, "type": "function", "gas": 6872}, {"name": "getTokenToEthInputPrice", "outputs": [{"type": "uint256", "name": "out"}], "inputs": [{"type": "uint256", "name": "tokens_sold"}], "constant": true, "payable": false, "type": "function", "gas": 5637}, {"name": "getTokenToEthOutputPrice", "outputs": [{"type": "uint256", "name": "out"}], "inputs": [{"type": "uint256", "name": "eth_bought"}], "constant": true, "payable": false, "type": "function", "gas": 6897}, {"name": "tokenAddress", "outputs": [{"type": "address", "name": "out"}], "inputs": [], "constant": true, "payable": false, "type": "function", "gas": 1413}, {"name": "factoryAddress", "outputs": [{"type": "address", "name": "out"}], "inputs": [], "constant": true, "payable": false, "type": "function", "gas": 1443}, {"name": "balanceOf", "outputs": [{"type": "uint256", "name": "out"}], "inputs": [{"type": "address", "name": "_owner"}], "constant": true, "payable": false, "type": "function", "gas": 1645}, {"name": "transfer", "outputs": [{"type": "bool", "name": "out"}], "inputs": [{"type": "address", "name": "_to"}, {"type": "uint256", "name": "_value"}], "constant": false, "payable": false, "type": "function", "gas": 75034}, {"name": "transferFrom", "outputs": [{"type": "bool", "name": "out"}], "inputs": [{"type": "address", "name": "_from"}, {"type": "address", "name": "_to"}, {"type": "uint256", "name": "_value"}], "constant": false, "payable": false, "type": "function", "gas": 110907}, {"name": "approve", "outputs": [{"type": "bool", "name": "out"}], "inputs": [{"type": "address", "name": "_spender"}, {"type": "uint256", "name": "_value"}], "constant": false, "payable": false, "type": "function", "gas": 38769}, {"name": "allowance", "outputs": [{"type": "uint256", "name": "out"}], "inputs": [{"type": "address", "name": "_owner"}, {"type": "address", "name": "_spender"}], "constant": true, "payable": false, "type": "function", "gas": 1925}, {"name": "name", "outputs": [{"type": "bytes32", "name": "out"}], "inputs": [], "constant": true, "payable": false, "type": "function", "gas": 1623}, {"name": "symbol", "outputs": [{"type": "bytes32", "name": "out"}], "inputs": [], "constant": true, "payable": false, "type": "function", "gas": 1653}, {"name": "decimals", "outputs": [{"type": "uint256", "name": "out"}], "inputs": [], "constant": true, "payable": false, "type": "function", "gas": 1683}, {"name": "totalSupply", "outputs": [{"type": "uint256", "name": "out"}], "inputs": [], "constant": true, "payable": false, "type": "function", "gas": 1713}]')

my_provider = Web3.HTTPProvider('https://mainnet.infura.io/v3/c534d76d934f40498f6d6113a46c6ab3')
w3 = Web3(my_provider)


"""1     IDEX  57849   55.5056% 0x2a0c0dbecc7e4d658f48e01e3fa353f44050c208
2     DEx.top   11628   11.1570% 0x7600977eb9effa627d6bd0da2e5be35e11566341
3     Ether Delta   6596    6.3288% 0x8d12a197cb00d4747a1fe03395095ce2a5cc6819
4     Bancor Network    6569    6.3029% ???
5     DDEX  5146    4.9375% 0x12459c951127e0c374ff9105dda097662a027093
6     Token Store   3750    3.5981% 0x1ce7ae555139c5ef5a57cc8d814a867ee6ee33d8
7     Star Bit  3448    3.3083% 0x12459c951127e0c374ff9105dda097662a027093
8     Kyber Network 2550    2.4467% ?????
9     Joyso 2205    2.1157% 0x04f062809b244e37e7fdc21d9409469c989c2342
10    Oasis Dex 1865    1.7894% 0x12459c951127e0c374ff9105dda097662a027093
11    Radar Relay   1303    1.2502% 0x12459c951127e0c374ff9105dda097662a027093
12    Paradex   820 0.7868% 0x12459c951127e0c374ff9105dda097662a027093
13    Airswap   243 0.2332% 0x8fd3121013a07c57f0d69646e86e7a4880b467b7
14    TokenJar  106 0.1017% 0x12459c951127e0c374ff9105dda097662a027093
15    The Ocean 91  0.0873% 0x12459c951127e0c374ff9105dda097662a027093
16    Erc dEX   25  0.0240% 0x12459c951127e0c374ff9105dda097662a027093
17    Enclaves  22  0.0211% 0xed06d46ffb309128c4458a270c99c824dc127f5d
18    Shark Relay   6   0.0058% 0x12459c951127e0c374ff9105dda097662a027093
19    Bamboo Relay  0   0.0000%
20    IDT Exchange  0   0.0000%
21    Tokenlon  0   0.0000%

Source: dexwatch Thus Sep 20 3:48PM EST
"""


dex_list = ["0x2a0c0dbecc7e4d658f48e01e3fa353f44050c208", # IDEX
            "0x7600977eb9effa627d6bd0da2e5be35e11566341", # DEx.top
            "0x8d12a197cb00d4747a1fe03395095ce2a5cc6819", # Etherdelta (done)
            "0x12459c951127e0c374ff9105dda097662a027093", # 0x v1 (done)
            "0x4f833a24e1f95d70f028921e27040ca56e09ab0b", # 0x v2 (done)
            "0x1ce7ae555139c5ef5a57cc8d814a867ee6ee33d8", # Token Store (done)
            "0x04f062809b244e37e7fdc21d9409469c989c2342", # Joyso
            "0x8fd3121013a07c57f0d69646e86e7a4880b467b7", # Airswap
            "0xed06d46ffb309128c4458a270c99c824dc127f5d", # Enclaves
           ]


bancor_relayers = open('data/bancor_relayers').read().strip().splitlines()
kyber_relayers = open('data/kyber_relayers').read().strip().splitlines()
uniswap_relayers = open('data/uniswap_relayers').read().strip().splitlines()

dex_list = dex_list + bancor_relayers + kyber_relayers + uniswap_relayers

def parse_address(raw_hex):
    """ Extract address from lowest hex bits, ignoring junk. """
    return raw_hex[-40:]

def parse_amount(raw_hex):
    return int(raw_hex, 16)

@persist_to_file('uniswap.dat')
def get_uniswap_token(address):
    token_addr = address
    erc20 = w3.eth.contract(address=Web3.toChecksumAddress('0x' + address), abi=UNISWAP_ABI)
    try:
        token_addr = erc20.functions.tokenAddress().call()
    except web3.exceptions.BadFunctionCallOutput: # todo handle chainsync errors?
        pass
    return token_addr.lower().replace("0x", "")

@persist_to_file('decimals.dat')
def get_decimals_for(address):
    if int(address, 16) == 0 or int(address, 16) == 1364068194842176056990105843868530818345537040110:
        return 18
    erc20 = w3.eth.contract(address=Web3.toChecksumAddress('0x' + address), abi=ERC20_ABI)
    try:
        decimals = int(erc20.functions.decimals().call())
    except web3.exceptions.BadFunctionCallOutput: # todo handle chainsync errors?
        return 0
    return decimals

@persist_to_file('labels.dat')
def get_node_label_for(address):
    if int(address, 16) == 0 or int(address, 16) == 1364068194842176056990105843868530818345537040110 or address.lower() == "c0829421c1d260bd3cb3e0f06cfe2d52db2ce315" or address.lower() == "c02aaa39b223fe8d0a0e5c4f27ead9083c756cc2" or address.lower() == "2956356cd2a2bf3202f771f50d3d14a367b48070":
        return ("ETH", "ETH")
    erc20 = w3.eth.contract(address=Web3.toChecksumAddress('0x' + address), abi=ERC20_ABI)
    name = "Unknown"
    symbol = "Unknown"
    try:
        name = erc20.functions.name().call()
    except OverflowError:
        pass
    except web3.exceptions.BadFunctionCallOutput:
        pass
    try:
        symbol = erc20.functions.symbol().call()
    except OverflowError:
        pass
    except web3.exceptions.BadFunctionCallOutput:
        pass
    return (symbol, "%s (%s)\n0x%s" % (name, symbol, address))

def parse_bancor(topics, data, address):
    tokenget_addr = parse_address(topics[1])
    tokenget,tokenget_label = get_node_label_for(tokenget_addr)
    amountget = (parse_amount(data[0:64]) / (10 ** get_decimals_for(tokenget_addr)))
    tokengive_addr = parse_address(topics[2])
    tokengive,tokengive_label = get_node_label_for(tokengive_addr)
    amountgive = (parse_amount(data[64:128]) / (10 ** get_decimals_for(tokengive_addr)))
    assert(len(data) == 192)
    return (tokenget_addr, tokenget_label, tokenget, amountget, tokengive_addr, tokengive_label, tokengive, amountgive)

def parse_etherdelta_clone(topics, data, address, data_length):
    tokenget_addr = parse_address(data[0:64])
    tokenget,tokenget_label = get_node_label_for(tokenget_addr)
    amountget = (parse_amount(data[64:128]) / (10 ** get_decimals_for(tokenget_addr)))
    tokengive_addr = parse_address(data[128:192])
    tokengive,tokengive_label = get_node_label_for(tokengive_addr)
    amountgive = (parse_amount(data[192:256]) / (10 ** get_decimals_for(tokengive_addr)))
    assert(len(data) == data_length)
    return (tokenget_addr, tokenget_label, tokenget, amountget, tokengive_addr, tokengive_label, tokengive, amountgive)

parse_etherdelta = lambda topics, data, address : parse_etherdelta_clone(topics, data, address, 384)
parse_tokenstore = lambda topics, data, address : parse_etherdelta_clone(topics, data, address, 448)

def parse_0x(topics, data, address):
    tokenget_addr = parse_address(data[128:192])
    tokenget,tokenget_label = get_node_label_for(tokenget_addr)
    amountget = (parse_amount(data[256:320]) / (10 ** get_decimals_for(tokenget_addr)))
    tokengive_addr = parse_address(data[64:128])
    tokengive,tokengive_label = get_node_label_for(tokengive_addr)
    amountgive = (parse_amount(data[192:256]) / (10 ** get_decimals_for(tokengive_addr)))
    assert(len(data) == 512)
    return (tokenget_addr, tokenget_label, tokenget, amountget, tokengive_addr, tokengive_label, tokengive, amountgive)

def parse_0x_v2(topics, data, address):
    abi_data = decode_abi(['address', 'address', 'uint256', 'uint256', 'uint256', 'uint256', 'bytes', 'bytes'], bytes(Web3.toBytes(hexstr=data)))
    tokenget_addr = parse_address(Web3.toHex(abi_data[-1])[2:])
    tokenget,tokenget_label = get_node_label_for(tokenget_addr)
    amountget = (parse_amount(data[192:256]) / (10 ** get_decimals_for(tokenget_addr)))
    tokengive_addr = parse_address(Web3.toHex(abi_data[-2])[2:])
    tokengive,tokengive_label = get_node_label_for(tokengive_addr)
    amountgive = (parse_amount(data[128:192]) / (10 ** get_decimals_for(tokengive_addr)))
    assert(len(data) >= 896)
    return (tokenget_addr, tokenget_label, tokenget, amountget, tokengive_addr, tokengive_label, tokengive, amountgive)

def parse_kyber(topics, data, address):
    abi_data = decode_abi(['address', 'address', 'uint256', 'uint256', 'address', 'uint256', 'address', 'address', 'bytes'], bytes(Web3.toBytes(hexstr=data)))
    tokenget_addr = parse_address(abi_data[0])
    tokenget,tokenget_label = get_node_label_for(tokenget_addr)
    amountget = (abi_data[2] / (10 ** get_decimals_for(tokenget_addr)))
    tokengive_addr = parse_address(abi_data[1])
    tokengive,tokengive_label = get_node_label_for(tokengive_addr)
    amountgive = (abi_data[3] / (10 ** get_decimals_for(tokengive_addr)))
    assert(len(data) >= 512)
    return (tokenget_addr, tokenget_label, tokenget, amountget, tokengive_addr, tokengive_label, tokengive, amountgive)

def parse_uniswap_tokenpurchase(topics, data, address):
    abi_data = decode_abi(['uint256', 'address', 'uint256', 'uint256'], Web3.toBytes(hexstr="".join([x.replace("0x", "") for x in topics])))
    tokenget_addr = get_uniswap_token(address[2:])
    tokenget,tokenget_label = get_node_label_for(tokenget_addr)
    amountget = (abi_data[-1] / (10 ** get_decimals_for(tokenget_addr)))
    tokengive_addr = "0"*40 # (eth given by definition)
    tokengive,tokengive_label = get_node_label_for(tokengive_addr)
    amountgive = (abi_data[-2] / (10 ** get_decimals_for(tokengive_addr)))
    assert(len(topics) == 4)
    return (tokenget_addr, tokenget_label, tokenget, amountget, tokengive_addr, tokengive_label, tokengive, amountgive)

def parse_uniswap_ethpurchase(topics, data, address):
    abi_data = decode_abi(['uint256', 'address', 'uint256', 'uint256'], Web3.toBytes(hexstr="".join([x.replace("0x", "") for x in topics])))
    tokenget_addr = "0"*40 # (eth gotten by definition)
    tokenget,tokenget_label = get_node_label_for(tokenget_addr)
    amountget = (abi_data[-1] / (10 ** get_decimals_for(tokenget_addr)))
    tokengive_addr = get_uniswap_token(address[2:])
    tokengive,tokengive_label = get_node_label_for(tokengive_addr)
    amountgive = (abi_data[-2] / (10 ** get_decimals_for(tokengive_addr)))
    assert(len(topics) == 4)
    return (tokenget_addr, tokenget_label, tokenget, amountget, tokengive_addr, tokengive_label, tokengive, amountgive)


def get_trade_data_from_log_item(topics, data, address):
    exchange = None
    parser = None
    if address == '0x8d12a197cb00d4747a1fe03395095ce2a5cc6819': # etherdelta
        # TODO handle clones
        if topics[0] == '0x6effdda786735d5033bfad5f53e5131abcced9e52be6c507b62d639685fbed6d': # trade log event
            exchange = "Etherdelta"
            parser = parse_etherdelta
    elif address == '0x1ce7ae555139c5ef5a57cc8d814a867ee6ee33d8': # Tokenstore
        if topics[0] == '0x3314c351c2a2a45771640a1442b843167a4da29bd543612311c031bbfb4ffa98':
            exchange = "Tokenstore"
            parser = parse_tokenstore
    elif address == '0x12459c951127e0c374ff9105dda097662a027093': # 0x v1
        if topics[0] == '0x0d0b9391970d9a25552f37d436d2aae2925e2bfe1b2a923754bada030c498cb3':
            exchange = "0x v1"
            parser = parse_0x
    elif address == '0x4f833a24e1f95d70f028921e27040ca56e09ab0b': # 0x v2
        if topics[0] == '0x0bcc4c97732e47d9946f229edb95f5b6323f601300e4690de719993f3c371129':
            exchange = "0x v2"
            parser = parse_0x_v2
    elif address in bancor_relayers:
        if topics[0] == '0x276856b36cbc45526a0ba64f44611557a2a8b68662c5388e9fe6d72e86e1c8cb':
            exchange = "Bancor"
            parser = parse_bancor
    elif address in kyber_relayers:
        if topics[0] == '0xd30ca399cb43507ecec6a629a35cf45eb98cda550c27696dcb0d8c4a3873ce6c':
            exchange = "Kyber"
            parser = parse_kyber
    elif address in uniswap_relayers:
        if topics[0] == '0x7f4091b46c33e918a0f3aa42307641d17bb67029427a5369e54b353984238705':
            exchange = "Uniswap"
            parser = parse_uniswap_ethpurchase
        if topics[0] == '0xcd60aa75dea3072fbc07ae6d7d856b5dc5f4eee88854f5b4abf7b680ef8bc50f' and len(topics) == 4: # (ZRXcoin has same event; eg https://etherscan.io/tx/0x3d774851984b665b6db16d8bbf7a138520c76db923599fc8929b29edd384db7b#eventlog)
            exchange = "Uniswap"
            parser = parse_uniswap_tokenpurchase
    else:
        # parsing failed
        return None

    if not parser:
        # no logs to parse
        return []

    # 1 log generated; return it
    (tokenget_addr, tokenget_label, tokenget, amountget, tokengive_addr, tokengive_label, tokengive, amountgive) = parser(topics, data, address)
    return [(tokenget_addr, tokenget_label, tokenget, amountget, tokengive_addr, tokengive_label, tokengive, amountgive, exchange)]
