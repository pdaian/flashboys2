# Arbitrage Data

This is the repository of data associated with the Flash Boys 2.0: Frontrunning, Transaction Reordering, and Consensus Instability in Decentralized Exchanges paper.

## Various Scripts

As you can see, there are various python scripts in the root of this repository. These scripts take the raw transaction data from the Etherum network as stored in a SQL DB and parse it to find information about gas auctions.

* calculate\_profit\_from\_logs.py - calculates arbitrage profits from solidity log events. Uses Google BigQuery dataset.
* calculate\_slots.py - calculate the price slots for gas auctions
* count\_wins.py - count the number of times each arbitrager won an auction
* csv\_hack.py - cleans data for parsing
* csv\_to\_sqlite.py - collates data from multiple CSVs into one database
* exchanges.py - scrapes and parses data from a list of well known distributed exchanges
* filter\_list.txt - list of addresses to ignore
* gastoken.py - script to identify if an arbitrager is using GasToken
* generate\_graphs.py - Generates various graphs
* get\_all\_arb\_receipts.py - Gets Ethereum transaction reciepts for successful arbitrageurs.
* get\_auction\_slots\_intersection.py - Gets reciepts for bidders to auctions.
* get\_bq\_blocks.py - Gets block data from Google BigQuery and puts it in a CSV.
* get\_bq\_fees.py - Gets block fee data from Google BigQuery and puts it in a CSV.
* get\_bq\_logs.py - Gets emitted logs and other transaction data from Google BigQuery and puts it in a CSV.
* get\_bq\_relayers.py - Gets emitted logs from the addresses for bancor, kyber and uniswap.
* get\_bq\_summarystats.py - Collates summary statistics from the BigQuery-scraped CSVs.
* get\_bq\_txlist.py - Gets various transaction data from Google BigQuery.
* get\_pairwise\_data.py - Pull out pairs of players in an auction from the auctions CSV.
* persistence.py - Helper function.
* read\_csv.py - Creates the auctions CSV from the raw collected data from the go-ethereum monitoring software.
* receipts.py - Helper function to write reciepts.
* scrape\_gasauctions.py - scrapes auctions from a full node by requesting block data.
* sqlite\_adapter.py - Helper function to query SQLite.
* update.py - Helper script to automate updating the dataset as time progresses.
* write\_csv.py - Connects to the SQL DB and retrieves the data from the SQL database and writes it out to a CSV for parsing.

## data

Contains a list of known relayers for various exchanges.

## etherdelta

Contains scripts to perform scraping of Etherdelta's transaction order book data.

## go-ethereum

This directory contains the source code for our fork of go-ethereum that we developed to monitor the ethereum network and collect transaction data as it propogated accross the network. Primarily the files that are of interest are:

* go-ethereum/eth/arb\_monitor.go
* go-ethereum/eth/MonitorListGetter 
* go-ethereum/eth/handler.go
* arbmonmon/

## graph\_templates

LaTeX source code for generating graphs (used for the paper).

## paper

The LaTeX source of the associated paper.

## webapp

The web application source code for the auction monitoring dashboard, which displays the data for monitoring of gas auctions as they happen.

