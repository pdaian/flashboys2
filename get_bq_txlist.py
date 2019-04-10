from exchanges import dex_list
import csv, os
from google.cloud import bigquery

FIELDS_TO_GRAB = 'block_number,transaction_hash,to_address,from_address,address,num_logs,gas,gas_price,receipt_gas_used,input,transaction_index'

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "etharbskey.json"
client = bigquery.Client()

query = "(SELECT " + FIELDS_TO_GRAB + " FROM "
query += "(SELECT "  + FIELDS_TO_GRAB.replace("num_logs,", "") + ", COUNT(*) AS num_logs FROM "
query += "(SELECT " + FIELDS_TO_GRAB.replace("num_logs,", "")
query += " FROM (SELECT " + FIELDS_TO_GRAB.replace("num_logs,", "").replace("block_number", "transactions.block_number").replace("transaction_index", "transactions.transaction_index")
query += """  FROM
  `bigquery-public-data.ethereum_blockchain.transactions` AS transactions
  JOIN `bigquery-public-data.ethereum_blockchain.logs` AS logs ON logs.transaction_hash = transactions.hash
WHERE TRUE
  AND NOT address = to_address
  AND address in UNNEST(@dex_list)
  AND NOT to_address IN UNNEST(@dex_list)
  )) GROUP BY block_number,transaction_hash,to_address,from_address,address,gas,gas_price,receipt_gas_used,input,transaction_index)) ORDER BY block_number ASC, transaction_index ASC;
"""

aqp = bigquery.ArrayQueryParameter('dex_list', 'STRING', dex_list)
query_params = [aqp]
job_config = bigquery.QueryJobConfig()
job_config.query_parameters = query_params
query_job = client.query(
    query,
    # Location must match that of the dataset(s) referenced in the query.
    location='US',
    job_config=job_config)  # API request - starts the query

# Print the results

addresses = set()

with open('data/all_success_arb_txs_bigquery.csv', 'w') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)

    spamwriter.writerow(FIELDS_TO_GRAB.split(","))
    for item in query_job:
        addresses.add(item['from_address'])
        spamwriter.writerow(item)

assert query_job.state == 'DONE'
print("[database fetcher] Wrote all BQ success data")

query = """SELECT block_number,transactions.hash,to_address,from_address,gas,gas_price,receipt_gas_used,input,transaction_index FROM 
  `bigquery-public-data.ethereum_blockchain.transactions` AS transactions
WHERE from_address IN UNNEST(@addrs)"""


aqp = bigquery.ArrayQueryParameter('addrs', 'STRING', [x.lower() for x in addresses])
query_params = [aqp]
job_config = bigquery.QueryJobConfig()
job_config.query_parameters = query_params
query_job = client.query(
    query,
    # Location must match that of the dataset(s) referenced in the query.
    location='US',
    job_config=job_config)  # API request - starts the query


with open('data/all_inclfail_arb_txs_bigquery.csv', 'w') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)

    spamwriter.writerow("block_number,transaction_hash,to_address,from_address,gas,gas_price,receipt_gas_used,input,transaction_index".split(","))
    for item in query_job:
        spamwriter.writerow(item)

assert query_job.state == 'DONE'
print("[database fetcher] Wrote all BQ incl fail data")

