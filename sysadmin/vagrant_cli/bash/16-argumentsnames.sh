#!/bin/bash

# run ./16-argumentsnames.sh X=1 Y=2 or ./16-argumentsnames.sh Y=1 X=2


for arg in "$@"; do
    index=$(echo $arg | cut -f1 -d=)
    val=$(echo $arg | cut -f2 -d=)
    case $index in
        X) x=$val ;;
        Y) y=$val ;;
        *) ;;
    esac
done
((result = x + y))
echo "X+Y=$result"
