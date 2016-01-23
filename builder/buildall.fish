#!/bin/bash
echo "Building $@"
sleep 5

number=$RANDOM

echo "Status $number"
let "number %= 2"

echo "Status $number"
exit $number
