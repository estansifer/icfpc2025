#!/bin/bash

prog="python3"
name="par_solve.py"
arg="8"
tries="3"

while true; do
    echo "Running $prog $name with arg $arg"
    "$prog" "$name" "$arg" "$tries"
    status=$?
    if [ $status -eq 0 ]; then
        exit 0
    fi
done
