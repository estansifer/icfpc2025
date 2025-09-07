#!/bin/bash

prog="python3"
name="par_solve.py"
arg="15"
tries="4"

while true; do
    echo "Running $prog $name with arg $arg"
    "$prog" "$name" "$arg" "$tries"
    sleep 1
done
