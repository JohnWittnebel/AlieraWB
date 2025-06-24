#!/bin/bash
GENERATIONS=4
CURR=0
while [ $CURR -le $GENERATIONS ]
do
    ./pipeline.sh
    CURR=$(($CURR + 1))
done
