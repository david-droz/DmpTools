#!/bin/bash


for site in CNAF BARI UNIGE
do
	xrdcp root://xrootd-dampe.cloud.ba.infn.it//MC/${site}.new /tmp/ddroz/
	RC=$?
	
	if [ "$RC" -ne 0 ]
	then
		echo "Do something"
	fi
	
	RES=$(sbatch slCrawler.sh ${site})
	
	jobID=${RES##* }
	
	while [ -f ${site}_${jobID}.running ]
	do
		sleep 30
	done
	
	if [ -f ${site}_${jobID}.failed ]
	then
		echo "Do something"
	fi
	
	if [ -f ${site}_${jobID}.complete ]
	then
		# db.ingest()
		rm /tmp/ddroz/${site}.new
	fi
	
done
