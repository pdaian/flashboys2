The file contract_addr.txt contains all the contracts (including EtherDelta contract itself) with successful trade transactions sent to it within [3900000, 5550000) 

for each file:

all_txs/all_txs-{begin_block}-{end_block}-1.txt

contains all the transactions sent to the addresses in contract_addr.txt in the block range [begin_block, end_block).

There are 5 coloumns in each file, each line represents one transaction:

BlockNumber TransactionHash From To GasPrice(Wei) GasUsed InputData


for each file:

succ_txs/succ_txs-{begin_block}-{end_block}-1.txt

contains all the transactions with one or more Etherdelta Trade Event in the block range [begin_block, end_block),

There are 6 coloumns in each file, each line represents one transaction:

BlockNumber TransactionHash Tag From To InputData


The Tag is one of { Trade, Arbitrage, Unknown}:

Trade means this transctions only generated one Trade Event, which means it is a normal trade transaction.

Arbitrage mean this transction generated exactly 2 Trade Events and the buy/sell tokens form a pair.

Otherwise, the transation will be tagged as Unknown.


