import csv, os
from google.cloud import bigquery

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "etharbskey.json"
client = bigquery.Client()


query = """SELECT DISTINCT logs.address FROM `bigquery-public-data.ethereum_blockchain.logs` AS logs JOIN UNNEST(topics) AS topic WHERE topic IN UNNEST(@topics)"""


for exchange in (('bancor', ['0x276856b36cbc45526a0ba64f44611557a2a8b68662c5388e9fe6d72e86e1c8cb']), ('kyber', ['0xd30ca399cb43507ecec6a629a35cf45eb98cda550c27696dcb0d8c4a3873ce6c']), ('uniswap', ['0x7f4091b46c33e918a0f3aa42307641d17bb67029427a5369e54b353984238705', '0xcd60aa75dea3072fbc07ae6d7d856b5dc5f4eee88854f5b4abf7b680ef8bc50f'])):
    outfile = 'data/' + exchange[0] + '_relayers'
    open(outfile, 'w').write('')
    topics = set(exchange[1])
    aqp = bigquery.ArrayQueryParameter('topics', 'STRING', topics)
    query_params = [aqp]
    job_config = bigquery.QueryJobConfig()
    job_config.query_parameters = query_params
    query_job = client.query(
        query,
        # Location must match that of the dataset(s) referenced in the query.
        location='US',
        job_config=job_config)  # API request - starts the query


    for item in query_job:
        open(outfile, 'a').write(item['address'] + '\n')

    assert query_job.state == 'DONE'
    print("[database fetcher] Wrote all %s relayers" % (exchange[0]))

