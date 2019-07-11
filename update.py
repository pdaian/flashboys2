import os, time

while True:
    print(time.time())

    os.system("python3 write_csv.py")
    os.system("python3 read_csv.py")
    #os.system("cp data/gas_slots.csv data/gas_slots_cache.csv")
    #os.system("python3 calculate_slots.py > slotout")
    #os.system("python3 get_auction_slots_intersection.py")
    os.system("python3 get_pairwise_data.py") # todo fix div by 0
    os.system("python3 get_bq_relayers.py")
    os.system("python3 get_bq_txlist.py")
    os.system("python3 get_bq_logs.py")
    os.system("python3 get_bq_blocks.py")
    os.system("python3 get_bq_fees.py")
    os.system("python3 get_bq_summarystats.py") # todo fix argv error
    os.system("rm -rf data/eth.csv")
    os.system("wget https://coinmetrics.io/data/eth.csv -O data/eth.csv")
    os.system("python3 calculate_profit_from_logs.py")
    os.system("python3 csv_to_sqlite.py")

    print(time.time())

    time.sleep(300 * 60)
