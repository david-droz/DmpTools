'''



'''

from __future__ import absolute_import, print_function, division

import json
import os
import sys
from glob import glob
from shutil import copy
import yaml
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from errorcodes import json_load_byteified

def incrementKey(dic,key,value):
	if key in dic.keys():
		dic[key] += value
	else:
		dic[key] = value

def isGood(f):
	if not f['good'] :
		return False
	if f['error_code'] != 0 :
		return False
	
	return True
	
def ekey(dic):
	def prefix(e):
		if np.log10(e) < 3:
			return str( int(e) ) + 'MeV'
		elif np.log10(e) < 6:
			return str( int(e/1e+3) ) + 'GeV'
		else:
			return str( int(e/1e+6) ) + 'TeV'
	emin = dic['emin']
	emax = dic['emax']
	return prefix(emin)+'-'+prefix(emax)
	
def getParticle(dic):
	
	particles = ['C','Electron','Gamma','He','Li','Muon','Proton']
	for p in particles:
		if p in dic['task']:
			return p
	
def fileStats(diclist,stats):
	
	stats['version'] = diclist[0]['version']
	
	all_bad_files = []
	
	bad_files = []
	
	for x in diclist:
		
		if not isGood(x): 
			all_bad_files.append(x['lfn'])
			continue
		
		if stats['version'] == '6.0.0' and "v5r4p2" in x['lfn']:
			bad_files.append(x['lfn'])
			continue
		elif stats['version'] == '5.4.2' and "v6r0p0" in x['lfn']:
			bad_files.append(x['lfn'])
			continue
		
		p = getParticle(x)
		e = ekey(x)
		
		#~ if "TeV" in e:
			#~ if not "1TeV" in e and not "10TeV" in e and not "100TeV" in e:
				#~ print(e)
				#~ print(x['lfn'])
				#~ raise Exception
		
		if x['task'] not in stats[x['type']].keys():
			stats[x['type']][x['task']] = {}
		if p not in stats[x['type']].keys():
			stats[x['type']][p] = {}
		if e not in stats[x['type']][p].keys():
			stats[x['type']][p][e] = {}
		
		if x['type'] == 'mc:reco':
			incrementKey(stats['mc:reco'][x['task']],'nevts',x['nevts'])
			incrementKey(stats['mc:reco'][p][e],'nevts',x['nevts'])
			
		elif x['type'] == 'mc:simu':
			incrementKey(stats['mc:simu'][x['task']],'nevts',x['nevts'])
			incrementKey(stats['mc:simu'][x['task']],'nfiles',1)
			incrementKey(stats['mc:simu'][x['task']],'size',x['size'])
			incrementKey(stats['mc:simu'][p][e],'nevts',x['nevts'])
			incrementKey(stats['mc:simu'][p][e],'nfiles',1)
			incrementKey(stats['mc:simu'][p][e],'size',x['size'])
			
	with open('wrongVersion.txt','w') as f:
		for item in bad_files:
			f.write(item + '\n')
			
	with open('wrongFiles.txt','w') as f:
		for item in all_bad_files:
			f.write(item + '\n')
	

def makeStatistics(l) :
	
	if not os.path.isdir('statistics'): os.mkdir('statistics')
	
	if os.path.isfile('statistics/stats.yaml'): return
	
	stats = { 'mc:reco': {}, 'mc:simu': {}}
	
	for f in l:
		with open(f,'rb') as myfile:
			diclist = json_load_byteified(myfile)
		fileStats(diclist,stats)
	
	yaml.dump(stats,open('statistics/stats.yaml','w'))
	
		
def makePlots():
	
	stats = yaml.load(open('statistics/stats.yaml','r'))
	
	for x in ['mc:reco','mc:simu']:
		outdir = 'statistics/'+x.replace(':','-')
		if not os.path.isdir(outdir): os.mkdir(outdir)
		
		for y in stats[x].keys():
			
			if not 'eV' in y:
				with open(outdir+'/particle_'+y+'.yaml','w') as f:
					yaml.dump(stats[x][y],f)
			else:
				with open(outdir+'/'+y+'.yaml','w') as f:
					yaml.dump(stats[x][y],f)
		
		##
		## Figure 1 : Number of events per species
		##
		
		species = {'C':0,'Electron':0,'Gamma':0,'He':0,'Li':0,'Muon':0,'Proton':0}
		
		for y in stats[x].keys():
			if not 'eV' in y: continue
			
			for z in species.keys():
				if z in y :
					species[z] += stats[x][y]['nevts']
					
		fig1 = plt.figure()
		rects = plt.bar(range(len(species)),species.values(),align='center',color='#1f77b4',alpha=0.7)
		plt.xticks(range(len(species)),species.keys())
		try:
			plt.yscale('log')
		except ValueError:
			plt.yscale('linear')
		plt.ylabel('Number of events')
		plt.title(stats['version']+ ' - ' + x +'\n Particle species')
		for rect in rects:
			h = int(rect.get_height())/1e+6
			plt.text(rect.get_x()+rect.get_width()/6.,1.05*rect.get_height(),'%d M'% h)
		
		plt.savefig('images/'+x.replace(':','-'))
		plt.close(fig1)
		
		
		###
		## Figure 2 : Number of events per energy range, for each species
		###
		
		for y in stats[x].keys():
			if 'eV' in y: continue
			
			if "BT" in y: continue
			
			md = {}
			
			for z in stats[x][y].keys():
				md[z] = stats[x][y][z]['nevts']
			
			if y == 'Proton':
				fig1 = plt.figure(figsize=(10,6))
			else:
				fig1 = plt.figure()
			rects = plt.bar(range(len(md)),md.values(),align='center',color='#1f77b4',alpha=0.7)
			plt.xticks(range(len(md)),md.keys())
			for rect in rects:
				h = int(rect.get_height())/1e+6
				plt.text(rect.get_x()+rect.get_width()/3.,1.05*rect.get_height(),'%d M'% h)
			try:
				plt.yscale('log')
			except ValueError:
				plt.yscale('linear')
			plt.ylabel('Number of events')
			titleName = stats['version']+ ' - ' + x +'\n' + y
			figName = 'images/'+x.replace(':','-')+'_'+y
			plt.title(titleName)
			
			if y == 'He':
				plt.ylim((1e+6,5e+8))
			elif y == 'Proton':
				plt.ylim((1e+7,3e+9))
			elif y in ['Electron','Gamma']:
				plt.xlim((-0.5,1.5))
				
			plt.savefig(figName)
			plt.close(fig1)
	

def main():
	if not os.path.isdir('images'): os.mkdir('images')
	
	list_of_json = []
	for x in sys.argv:
		if '.json' in x or '.yaml' in x:
			list_of_json.append(x)
		elif '.txt' in x:
			with open(x,'r') as f:
				for line in f:
					list_of_json.append(line.replace('\n',''))
	
	makeStatistics(list_of_json)	
	makePlots()		


if __name__ == '__main__' :
	
	main()
