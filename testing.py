import csv, os
from google.cloud import bigquery

FIELDS_TO_GRAB = 'block_number,transaction_hash,to_address,from_address,num_logs,gas,gas_price,receipt_gas_used,input,transaction_index'


addresses = set(['0x0000bAA8F700aF2476492b19e378d61b90454982'])


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "etharbskey.json"
client = bigquery.Client()





query = """SELECT block_number,transactions.hash,to_address,from_address,gas,gas_price,receipt_gas_used,input,transaction_index FROM 
  `bigquery-public-data.ethereum_blockchain.transactions` AS transactions
WHERE from_address IN UNNEST(@addrs) """


aqp = bigquery.ArrayQueryParameter('addrs', 'STRING', [x.lower() for x in ['0x0000bAA8F700aF2476492b19e378d61b90454982']])
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
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)

    spamwriter.writerow(FIELDS_TO_GRAB.split(","))
    for item in query_job:
        spamwriter.writerow(item)

assert query_job.state == 'DONE'
print("[database fetcher] Wrote all BQ incl fail data")

