#!/bin/bash

prog="python3"
name="par_solve.py"
arg="5"
# tries="3"

while true; do
    echo "Running $prog $name with arg $arg"
    "$prog" "$name" "$arg"
    status=$?
    if [ $status -eq 0 ]; then
        exit 0
    fi
    sleep 1
done
