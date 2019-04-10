import csv, os
from google.cloud import bigquery

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "etharbskey.json"
client = bigquery.Client()


FIELDS_TO_GRAB = 'number,timestamp,gas_limit,gas_used,miner,extra_data'

query = """SELECT """ + FIELDS_TO_GRAB +  """ FROM `bigquery-public-data.ethereum_blockchain.blocks`;"""


with open('data/block_data.csv', 'w') as csvfile:
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
print("[database fetcher] Wrote all block data")

