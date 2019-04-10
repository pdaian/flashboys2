import csv, os
from google.cloud import bigquery
from exchanges import dex_list

FIELDS_TO_GRAB = 'block_number,transaction_hash,to_address,from_address,address,num_logs,gas,gas_price,receipt_gas_used,input,transaction_index'

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "etharbskey.json"
client = bigquery.Client()

txs = set(['0xe1844a185ced1361f7e695b589f8dc1f9c917e7e85c08825bd192d079e3c4cd6'])


query = """SELECT log_index,transaction_hash,logs.transaction_index,address,data,topics,logs.block_timestamp,logs.block_number FROM 
  `bigquery-public-data.ethereum_blockchain.logs` AS logs
  JOIN `bigquery-public-data.ethereum_blockchain.transactions` AS transactions ON logs.transaction_hash = transactions.hash
WHERE NOT logs.address = transactions.to_address
  AND logs.address in UNNEST(@dex_list)
  AND NOT transactions.to_address IN UNNEST(@dex_list) ORDER BY block_number ASC, transaction_index ASC"""

aqp = bigquery.ArrayQueryParameter('dex_list', 'STRING', dex_list)
query_params = [aqp]
job_config = bigquery.QueryJobConfig()
job_config.query_parameters = query_params
query_job = client.query(
    query,
    # Location must match that of the dataset(s) referenced in the query.
    location='US',
    job_config=job_config)  # API request - starts the query


with open('data/all_logs_bigquery.csv', 'w') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)

    spamwriter.writerow("log_index,transaction_hash,transaction_index,address,data,topics,block_timestamp,block_number".split(","))
    for item in query_job:
        spamwriter.writerow(item)

assert query_job.state == 'DONE'
print("[database fetcher] Wrote all logs")

