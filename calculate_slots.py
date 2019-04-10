from statistics import mean
import csv
import numpy as np

import csv_hack

arbitrageurs = {}
slotprices = {}

def add_to_count(arbitrageurs, arbitrageur):
    if arbitrageur in arbitrageurs:
        arbitrageurs[arbitrageur] += 1
    else:
        arbitrageurs[arbitrageur] = 1

slotsdict = csv.DictReader(open('data/gas_slots_6207336_6146507.csv'))
slotsdict = csv.DictReader(open('data/gas_slots.csv'))
for tx in slotsdict:
    slot = int(tx['tx_position'])
    if int(tx['gas_used']) < (int(tx['gas_limit']) * 0.6) and int(tx['gas_price']) > 310000000000 and tx['log_topics'].count("~") > 1 and not tx['to'].lower() in ["0xa62142888aba8370742be823c1782d17a0389da1", "0xdd9fd6b6f8f7ea932997992bbe67eabb3e316f3c"]:
        print(tx['hash'], tx['from'], tx['to'])
        add_to_count(arbitrageurs, tx['from'])
    if not slot in slotprices:
        slotprices[slot] = []
    slotprices[slot].append(int(tx['gas_price']))

for arbitrageur in arbitrageurs.keys():
    if arbitrageurs[arbitrageur] > 0:
        print("arber", "https://etherscan.io/address/" + arbitrageur, arbitrageurs[arbitrageur])

open("data/slots_new.csv", "w").write("\n".join([",".join([str(x/(10**9)) for x in [ np.percentile(slotprices[slot], 10), np.percentile(slotprices[slot], 50), np.percentile(slotprices[slot], 75), np.percentile(slotprices[slot], 90), np.percentile(slotprices[slot], 99)]]) for slot in range(0, 10)]))
for slot in slotprices:
    prices = slotprices[slot]
    print(slot, np.percentile(prices, 10), np.percentile(prices, 50), np.percentile(prices, 75), np.percentile(prices, 99))
