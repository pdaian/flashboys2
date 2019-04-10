import csv
i = 0
senders = {}
start_id = 251975668
with open('attack.csv', 'r' ) as f:
    i += 1
    if i % 10000 == 0:
        print(i)
    reader = csv.DictReader(f)
    for line in reader:
        sender= line['sender']
        if len(sender) > 10:
            if sender not in senders:
                senders[sender] = 0
            senders[sender] += 1


print(senders)
