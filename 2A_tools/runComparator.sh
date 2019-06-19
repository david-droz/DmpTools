#!/bin/bash

if [ $# -lt 2 ]; then
  echo 1>&2 "$0: not enough arguments"
  exit 2
elif [ $# -gt 2 ]; then
  echo 1>&2 "$0: too many arguments"
  exit 2
fi

source /cvmfs/dampe.cern.ch/rhel6-64/etc/setup.sh
dampe_init

mkdir evtdisplays 2>/dev/null

for i in 1 2 3
do
	python compare.py ${1} ${2}
done

BSN=$(basename ${1})

dmp-validate selected/${BSN/".root"/"_UserSel.root"} >/dev/null 2>&1

mv validation_plots.root evtdisplays/${BSN/".root"/"_displays.root"} 
