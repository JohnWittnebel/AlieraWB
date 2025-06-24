#!/bin/bash
#Step -1: create new folder for local machine to store results to
NUMITEMS=$(ls ./AI/trainingData | wc -l | awk '{print $1}')

if [ $NUMITEMS -ge 12 ]
then
    cd AI/trainingData/
    rm -rf trainingDataSubfolder0
    rm -rf trainingDataSubfolder1
    k=2
    while [ $k -lt $NUMITEMS ]
    do
        mv trainingDataSubfolder$k trainingDataSubfolder$(($k-2))
        k=$(($k+1))
    done
    cd ../..
fi

NEWDIR="trainingDataSubfolder"
NEWDIR="${NEWDIR}$NUMITEMS"
cd ./AI/trainingData/
mkdir $NEWDIR
cd ../..

#Step 0: start cloud if not active

python3 startInstance.py
sleep 8

# NOTE: this only works with the specific configuration that exists. Might need to update
TABLE=$(~/Downloads/google-cloud-sdk/bin/gcloud compute instances list --project symmetric-axle-384300)
ExtIP=0
i=0
for datum in $TABLE
do
    if [ $i -eq 11 ]
    then
        ExtIP=$datum
    fi
    i=$((i+1))
done
echo $ExtIP

#Step 1: assign work to cloud through ssh

scp -i ~/.ssh/gckey -o StrictHostKeyChecking=no ./AI/botModels/currbot.bot wittnebeljohn@$ExtIP:~/aliera/AI/botModels/currbot.bot
echo "############ connecting to VM ############"
ssh -i ~/.ssh/gckey -o StrictHostKeyChecking=no wittnebeljohn@$ExtIP -f 'cd aliera; screen -d -m; ./worker.sh 200 100 > /dev/null'
echo "############     exited VM    ############"

#Step 2: run test.py with proportional work (like 100 to 160), approx 30min -> 46 generations/day potentially

python3 test.py 70 10

#Step 3: retrieve data from VM, shutdown VM

scp -i ~/.ssh/gckey -o StrictHostKeyChecking=no wittnebeljohn@$ExtIP:~/aliera/AI/data.zip .
while [ $? -eq 1 ];
do
    python3 test.py 10 10
    scp -i ~/.ssh/gckey -o StrictHostKeyChecking=no wittnebeljohn@$ExtIP:~/aliera/AI/data.zip .
done

echo '############ connecting to VM ############'
ssh -i ~/.ssh/gckey -o StrictHostKeyChecking=no wittnebeljohn@$ExtIP 'cd aliera/AI; rm data.zip; sudo shutdown -h now'
echo '############    exited VM    #############'

#Step 4: move data into appropriate folder

unzip data.zip
rm data.zip
cd AI/trainingData

NUMITEMS=$(ls | wc -l | awk '{print $1}')
mv ../../trainingData ./trainingDataSubfolder$NUMITEMS

#Step 5: train new generation
cd ../..
python3 test.py train

#Step 6: verify new generation is better
python3 startInstance.py
sleep 8

# NOTE: this only works with the specific configuration that exists. Might need to update
TABLE=$(~/Downloads/google-cloud-sdk/bin/gcloud compute instances list --project symmetric-axle-384300)
ExtIP=0
i=0
for datum in $TABLE
do
    if [ $i -eq 11 ]
    then
        ExtIP=$datum
    fi
    i=$((i+1))
done
echo $ExtIP

scp -i ~/.ssh/gckey -o StrictHostKeyChecking=no ./AI/botModels/nextbot.bot wittnebeljohn@$ExtIP:~/aliera/AI/botModels/nextbot.bot
echo '############ connecting to VM ############'
ssh -i ~/.ssh/gckey -o StrictHostKeyChecking=no wittnebeljohn@$ExtIP -f 'cd aliera; screen -d -m; ./verification.sh > /dev/null'
echo '############     exited VM    ############'

python3 test.py verify

scp -i ~/.ssh/gckey -o StrictHostKeyChecking=no wittnebeljohn@$ExtIP:~/aliera/resultFile.txt ./resultFile2.txt
while [ $? -eq 1 ];
do
    sleep 60
    scp -i ~/.ssh/gckey -o StrictHostKeyChecking=no wittnebeljohn@$ExtIP:~/aliera/resultFile.txt ./resultFile2.txt
done

echo '############ connecting to VM ############'
ssh -i ~/.ssh/gckey -o StrictHostKeyChecking=no wittnebeljohn@$ExtIP 'cd aliera/AI; rm data.zip; sudo shutdown -h now'
echo '############    exited VM    #############'
