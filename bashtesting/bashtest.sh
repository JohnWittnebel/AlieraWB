#!/bin/bash

TABLE=$(~/Downloads/google-cloud-sdk/bin/gcloud compute instances list --project symmetric-axle-384300)
i=0
for picklefile in $TABLE
do
    if [ $i -eq 11 ]
    then
        echo $picklefile
    fi
    i=$((i+1))
done
