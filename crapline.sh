#!/bin/bash
cd AI
NUMLOCAL=$(ls trainingData | wc -l)
i=$(($NUMLOCAL))

for picklefile in $(ls trainingData2)
do
    mv trainingData2/$picklefile ./trainingData/pos${i}.pickle
    i=$(($i+1))
done

rmdir trainingData2

#Step 5: train, verify that new generation is better
cd ..
python3 test.py train 
