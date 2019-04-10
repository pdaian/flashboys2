import csv
def get_winner_dict():
    winner_dict = {}
    slotsdict = csv.DictReader(open('data/slot_auction.csv'))
    for slot in slotsdict:
        slot['log_count'] = slot['log_addrs'].count("~") + min(1, len(slot['log_addrs']))
        winner_dict[slot['hash']] = slot
    return winner_dict


arbs = {}

winner_dict = get_winner_dict()
print(len(winner_dict.keys()))

for hash in winner_dict:
    if winner_dict[hash]['log_count'] > 0:
        sender = winner_dict[hash]['from']
        if not sender in arbs:
            arbs[sender] = 0
        arbs[sender] += 1

print(arbs)
