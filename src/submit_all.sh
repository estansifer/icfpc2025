#!/bin/bash

prog="python3"
name="dfs_no_batch.py"

for i in $(seq 6 15); do
    echo "Running $prog $name with arg $i"
    "$prog" "$name" "$i" > out
done
