'''

Initial problem: two files have not the same number of events, but they were expected to.

This program looks for the events present in one file but not the other, based on timestamp.

Usage:
> bash runComparator.sh file1.root file2.root

	Order of files does not matter

Output:
	a .root file under ./selected/
	event displays under ./evtdisplays/<infile>_displays.root

'''

from __future__ import division, absolute_import, print_function

import sys
import os

if sys.version_info[0] == 2:			# Python2 / Python3 compatibility
	range = xrange
	import cPickle as pickle 
else:
	import pickle

def extractTimeStamps(f,out):
	'''
	Build a list that contains all timestamps for a given file and saves it to a pickle file
	'''
	from ROOT import gSystem
	gSystem.Load('libDmpEvent.so')
	from ROOT import DmpChain
	
	dmpch = DmpChain("CollectionTree");
	dmpch.Add(f)
	
	a = []
	for i in range(dmpch.GetEntries()):
		
		pev = dmpch.GetDmpEvent(i)
		
		sec = pev.pEvtHeader().GetSecond()
		msec = pev.pEvtHeader().GetMillisecond()
		if msec >= 1. :
			msec = msec / 1000.
		a.append(sec + msec)
		
		del pev
	
	with open(out,'wb') as f:
		pickle.dump(a,f)
		
	dmpch.Terminate()

def compare(f1,f2,out1,out2):
	'''
	Loads pickle files from extractTimeStamps, identifies differences and then saves DmpEvents corresponding to them
	'''
	
	###
	def _doComparison(f,indices):
		from ROOT import gSystem
		gSystem.Load('libDmpEvent.so')
		from ROOT import DmpChain
		dmpch = DmpChain("CollectionTree")
		dmpch.Add(f)
		counter = 0
		dmpch.SetOutputDir('selected')
		for i in indices:
			pev = dmpch.GetDmpEvent(i)
			dmpch.SaveCurrentEvent()
			counter += 1
		print("Events selected: ", counter)	
		dmpch.Terminate()
	### end function
	
	with open(out1,'rb') as f:
		times1 = pickle.load(f)
	with open(out2,'rb') as f:
		times2 = pickle.load(f)
	
	# Symmetry: don't know which file is the first one	
	if len(times2) > len(times1):
		diffs = list( set(times2) - set(times1) )
		print("Found ", len(diffs), " different events")
		evtindices = [times2.index(x) for x in diffs]
		_doComparison(f2,evtindices)
	else:
		diffs = list( set(times1) - set(times2) )
		print("Found ", len(diffs), " different events")
		evtindices = [times1.index(x) for x in diffs]
		_doComparison(f1,evtindices)
	

if __name__ == '__main__' :
	
	if not os.path.isdir('junk'): os.mkdir('junk')
	
	filename1 = os.path.basename(sys.argv[1])
	filename2 = os.path.basename(sys.argv[2])
	
	outname1 = 'junk/'+filename1.replace('.root','.1.pick')
	outname2 = 'junk/'+filename2.replace('.root','.2.pick')
	
	if not os.path.isfile(outname1) and not os.path.isfile(outname2):
		extractTimeStamps(sys.argv[1],outname1)
	elif os.path.isfile(outname1) and not os.path.isfile(outname2):
		extractTimeStamps(sys.argv[2],outname2)
	elif not os.path.isfile(outname1) and os.path.isfile(outname2):
		extractTimeStamps(sys.argv[1],outname1)
	else:
		compare(sys.argv[1],sys.argv[2],outname1,outname2)
