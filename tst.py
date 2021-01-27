import os
import glob

S = "PTF10"

def find_cands(PATH):
	bla = []
	for dirpath,dirnames,filenames in os.walk(PATH):
		for f in filenames:
			ff = os.path.join(dirpath,f)
			#print os.path.splitext(ff)
			if ff.endswith('all.cand'):
			#if os.path.splitext(ff)[-1] == 'all.cand':
				bla.append(ff)
	return bla

def find_phil(PATH):
	phils = []
	for dirpath,dirnames,filenames in os.walk(PATH):
		for f in filenames:
			ff = os.path.join(dirpath,f)
			if os.path.splitext(ff)[-1] == '.fil':
				phils.append(ff)
	return phils

bigdir = '/beegfsEDD/PAF/PAF/RESULTS/'
otherbigdir = '/beegfsEDD/PAF/PAF/SEARCH/'
#print os.path.join(bigdir,S+"*")
Source = glob.glob(os.path.join(bigdir,S+"*"))
#print Source
for d in Source:
	D = find_cands(d)
	print "CANDIDATE FILE"
	print D[0]
	print "DIRECTORY"
	print os.path.join(os.path.dirname(D[0]),"CANDS")
	X = D[0].split(os.sep)[5]
	time = X.split('_')[-1]	
	tt = "{}-{}-{}T{}:{}:{}".format(time[0:4],time[4:6],time[6:8],time[9:11],time[11:13],time[13:15])
	s = X.split('_')[0]
	tmpdir = os.path.join(otherbigdir,tt+"*"+s)
	F = glob.glob(tmpdir)
	ph = find_phil(F[0])
	print "FILTERBANK FILES"
	print ph

