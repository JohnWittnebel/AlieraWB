#!/bin/bash
NUMITEMS=$(ls ./AI/trainingData | wc -l | awk '{print $1}')
NEWDIR="trainingDataSubfolder"
NEWDIR="${NEWDIR}$NUMITEMS"
cd AI/trainingData/
mkdir $NEWDIR
cd ../..
