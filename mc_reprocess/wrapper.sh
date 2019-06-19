#!/bin/bash
wd=$(pwd)
echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
echo "HOSTNAME: $(hostname -f)"
echo "SLURM ARRAY JOB ID : ${SLURM_ARRAY_JOB_ID}"
echo "SLURM ARRAY TASK ID: ${SLURM_ARRAY_TASK_ID}"
echo "SWPATH: ${SWPATH}"
echo "SCRATCH: ${SCRATCH}"
echo "WORKDIR: ${WORKDIR}"
echo "LOG LEVEL: ${DAMPE_LOGLEVEL}"
echo "start time: $(date)"
echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
if [ ! -f /etc/centos-release ]
then
	echo "Sourcing SL6"
	source /cvmfs/dampe.cern.ch/rhel6-64/etc/setup.sh
else
	if grep -q "release 7." /etc/centos-release
	then
		echo "Sourcing CentOS7"
		source /cvmfs/dampe.cern.ch/centos7/etc/setup.sh
	else
		echo "Sourcing SL6"
		source /cvmfs/dampe.cern.ch/rhel6-64/etc/setup.sh
	fi
fi
cd ${SWPATH}
source bin/thisdmpsw.sh
WORK_DIR=$(mktemp -d -p ${SCRATCH})
cd ${WORK_DIR}
## EXECUTABLE BELOW ##
time python ${DMPSWSYS}/share/TestRelease/JobOption_MC_DigiReco_Prod.py -y ${WORKDIR}/chunk_${SLURM_ARRAY_TASK_ID}.yaml
echo "stop time: $(date)"
echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
echo "cleanup..."
cd ${SCRATCH}
rm -vrf ${WORK_DIR}
echo "all done. good bye!"
echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
cd ${WORKDIR}
