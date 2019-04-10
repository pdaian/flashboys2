#!/usr/bin/env bash

onexit() {
    kill -TERM -0
    wait
}
trap onexit INT

set -x

for (( i=3900000; i<5550000; i+=10000))
do
    python3 find_all_txs.py --st $i --len 10000 --r 1 &

done

wait

#python3 find_succ_txs.py --st 3900000 --len 100000 --r 20
