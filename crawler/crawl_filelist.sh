#!/usr/bin/env bash
# RELIES ON $CRAWLER variable
release="latest"
infile=$1
global_badfile=$2

ofile=${infile/".txt"/".json"}
errfile=${ofile/".json"/".err"}
badfile_tmp=${ofile/".json"/".bad"}

rm -f ${errfile} ${badfile_tmp}

if [ "${HOSTNAME}" = "gridvm7.unige.ch" ]
then
	source /cvmfs/dampe.cern.ch/centos7/etc/setup.sh
	echo "Using centos7"
elif grep -q "CentOS" /etc/redhat-release
then
	source /cvmfs/dampe.cern.ch/centos7/etc/setup.sh
	echo "Using centos7"
else
	source /cvmfs/dampe.cern.ch/rhel6-64/etc/setup.sh
	echo "Using SL6"
fi
dampe_init ${release}

for f in $(cat ${infile});
do
    #python ${CRAWLER_ROOT}/crawler.py ${f} -o ${ofile} 2> ${errfile}
    python ${CRAWLER_ROOT}/crawler.py ${f} -o ${ofile}
    RC1=$?
done

python ${CRAWLER_ROOT}/analyze.py ${ofile} ${badfile_tmp} 2> ${errfile}
RC2=$?

if [ -f ${badfile_tmp} ];
then
    cat ${badfile_tmp} >> ${global_badfile}
fi

python ${CRAWLER_ROOT}/errorcodes.py ${ofile}
RC3=$?

RC=$(( RC1 + RC2 + RC3 ))

exit ${RC}
