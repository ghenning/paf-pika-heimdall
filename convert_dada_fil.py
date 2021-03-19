import os
import argparse
import glob
import subprocess

# finds all .dada files in PATH
def find_dad(PATH):
	dads = []
	for dirpath,dirnames,filenames in os.walk(PATH):
		for f in filenames:
			ff = os.path.join(dirpath,f)
			if os.path.splitext(ff)[-1] == '.dada':
				#print ff # this is the file to convert
				#print ff.split(os.sep)[-3].split('M')[-1] # this is the beam number
				dads.append(ff)
	return dads

# finds all .fil in PATH
def find_phil(PATH):
	dads = []
	for dirpath,dirnames,filenames in os.walk(PATH):
		for f in filenames:
			ff = os.path.join(dirpath,f)
			if os.path.splitext(ff)[-1] == '.fil':
				#print ff # this is the file to convert
				#print ff.split(os.sep)[-3].split('M')[-1] # this is the beam number
				dads.append(ff)
	return dads
#p = '/beegfsEDD/PAF/PAF/SEARCH/2020-08-03T00:32:06.194_B0355-54'
#D = find_dad(p)
#for dad in D:
#	print dad

if __name__=="__main__":
	desc = """ Convert PAF dada files to filterbanks """
	parser = argparse.ArgumentParser(description=desc)
	parser.add_argument('--dir',type=str,help='Directory of PAF source, this is just thought as a test case to try out on a single directory')
	parser.add_argument('--source',type=str,help='Convert all for one source, use this to convert all pointings of a source')
	parser.add_argument('--sourcebeams',type=str,help='Fix beam numbers in filterbanks, use this to fix the beam numbers of a source for Heimdall')
	args = parser.parse_args()
	# 
	# finds .dada files and converts them to .fil using dspsr digifil
	# since this is done from a docker container the output files
	# will be owned by root:root, so we chown it to pulsar group

	# this runs for the --dir option
	if not args.dir==None:
		D = find_dad(args.dir)
		for dad in D:
			print "original {}".format(dad)
			dad_name = os.path.basename(dad)
			#print "file name {}".format(dad_name)
			dad_dir = os.path.dirname(dad)
			#print "dir path {}".format(dad_dir)
			dad_noext = os.path.splitext(os.path.basename(dad))[0]
			#print "name no extension {}".format(dad_noext)
			#dad_fil = os.path.join(dad_dir,dad_noext + ".fil")
			#print "new fil name {}".format(dad_fil)
			dad_beam = dad.split(os.sep)[-3].split('M')[-1]
			#print dad_beam
			dad_source = dad.split(os.sep)[-4].split('_')[1]
			#print dad_source
			dad_time = dad.split(os.sep)[-4].split('.')[0]
			dad_time = dad_time.replace('-','').replace(':','')
			#print dad_time
			dad_fil = "{}_{}_BEAM_{}.fil".format(dad_source,dad_time,dad_beam)
			#print dad_fil
			dad_fil = os.path.join(dad_dir,dad_fil)
			print "new {}".format(dad_fil)
			#subprocess.check_call(["ls",os.path.dirname(dad)])
			# call digifil to convert 
			subprocess.check_call(["digifil","-b","8","-o",dad_fil,dad])
			#subprocess.check_call(["chown","50000:50000",dad_fil]) # old pulsar account
			subprocess.check_call(["chown","4875:6850",dad_fil]) 
			subprocess.check_call(["chmod","g=u",dad_fil]) 
	# this runs for the --source option
	if not args.source==None:
		bigdir = '/beegfsEDD/PAF/PAF/SEARCH/'
		Source = glob.glob(os.path.join(bigdir,"*"+args.source))
		#print Source
		#for x in Source:
		#	print x.split(os.sep)[-1]
		for d in Source:
			D = find_dad(d)
			for dad in D:
				print "original {}".format(dad)
				dad_name = os.path.basename(dad)
				dad_dir = os.path.dirname(dad)
				dad_noext = os.path.splitext(os.path.basename(dad))[0]
				dad_beam = dad.split(os.sep)[-3].split('M')[-1]
				dad_source = dad.split(os.sep)[-4].split('_')[1]
				dad_time = dad.split(os.sep)[-4].split('.')[0]
				dad_time = dad_time.replace('-','').replace(':','')
				dad_fil = "{}_{}_BEAM_{}.fil".format(dad_source,dad_time,dad_beam)
				dad_fil = os.path.join(dad_dir,dad_fil)
				print "new {}".format(dad_fil)
				subprocess.check_call(["digifil","-b","8","-o",dad_fil,dad])
			    #subprocess.check_call(["chown","50000:50000",dad_fil]) # old pulsar account
			    subprocess.check_call(["chown","4875:6850",dad_fil]) 
	# this runs for the --sourcebeams option
	if not args.sourcebeams==None:
		bigdir = '/beegfsEDD/PAF/PAF/SEARCH/'
		Source = glob.glob(os.path.join(bigdir,"*"+args.sourcebeams))
		for d in Source:
			D = find_phil(d)
			for phil in D:
				#print phil
				phil_beam = phil.split(os.sep)[-3].split('M')[-1]
				phil_beam = str(int(phil_beam)+1)
				print phil_beam
				subprocess.check_call(["filedit","-b",phil_beam,phil])
