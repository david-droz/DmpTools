#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --partition=debug
#SBATCH --mem=4G

trap term_handler SIGTERM

term_handler()
{
	rm ${1}_${SLURM_JOB_ID}.running
	touch rm ${1}_${SLURM_JOB_ID}.failed
	
	exit -1
	
}

touch ${1}_${SLURM_JOB_ID}.running


srun python SOMETHING /tmp/ddroz/${1}.new


rm ${1}_${SLURM_JOB_ID}.running
touch ${1}_${SLURM_JOB_ID}.complete

