import csv, os
from google.cloud import bigquery

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "etharbskey.json"
client = bigquery.Client()


FIELDS_TO_GRAB = 'block_number,total_fees'

query = """SELECT block_number,SUM(((CAST(receipt_gas_used as INT64)) * (CAST(gas_price as INT64)/1000000000))/1000000000) as total_fees FROM `bigquery-public-data.ethereum_blockchain.transactions` GROUP BY block_number;"""


with open('data/block_fees.csv', 'w') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)

    spamwriter.writerow(FIELDS_TO_GRAB.split(","))

    job_config = bigquery.QueryJobConfig()
    query_job = client.query(
        query,
        # Location must match that of the dataset(s) referenced in the query.
        location='US',
        job_config=job_config)  # API request - starts the query


    for item in query_job:
        spamwriter.writerow([item[x] for x in FIELDS_TO_GRAB.split(',')])


assert query_job.state == 'DONE'
print("[database fetcher] Wrote all block fees")

