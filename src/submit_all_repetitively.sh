#!/bin/bash

prog="python3"
name="par_solve.py"
arg="14"
tries="3"

while true; do
    echo "Running $prog $name with arg $arg"
    "$prog" "$name" "$arg" "$tries"
    sleep 1
    status=$?
    if [ $status -eq 0 ]; then
        exit 0
    fi
done
