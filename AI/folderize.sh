#!/bin/bash
j=3

while [ $j -le 7 ]
do
    cd trainingData/trainingDataSubfolder$j
    i=0
    while [ $i -le 99999 ]
    do
        mv pos$(($i+($j*100000))).pickle pos$i.pickle
        i=$(($i + 1))
    done
    cd ../..
    j=$(($j + 1))
done
