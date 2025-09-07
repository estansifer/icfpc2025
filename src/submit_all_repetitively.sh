#!/bin/bash

prog="python3"
name="par_solve.py"
arg="7"
tries="3"

while true; do
    echo "Running $prog $name with arg $arg"
    "$prog" "$name" "$arg" "$tries"
done
