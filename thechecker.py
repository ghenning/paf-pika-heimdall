from astropy.time import Time
import sys
from datetime import datetime, timedelta
import glob
import os

def check_between(body,outdir):
    basename = os.path.splitext(os.path.basename(body))[0]
    EmmJD = basename.split('_')[1]
    beam = int(basename.split('_')[3])

    candfiles = glob.glob(os.path.join(outdir,"*.cand"))

    for f in candfiles:
        candbase = os.path.splitext(os.path.basename(f))[0]
        candtime = candbase.split('_')[0]
        candbeam = int(candbase.split('_')[1])

        if beam != candbeam:
            #print("wrong beam")
            continue

        T = Time(float(EmmJD),format='mjd')
        T_utc = T.utc.iso
        t = T_utc.replace(' ', '-')

        starttime = datetime.strptime(t,'%Y-%m-%d-%H:%M:%S.%f')
        endtime = starttime + timedelta(minutes=3.8)

        check_me = datetime.strptime(candtime, '%Y-%m-%d-%H:%M:%S')
        if check_me>starttime and check_me<endtime:
            #print("already processed")
            return True
        else:
            #print("wrong time")
            continue

if __name__ == '__main__':
    body = os.path.join(os.getcwd(),'I_58228.02102273_beam_10_8bit.fil')
    outdir = os.path.join(os.getcwd(),'bla')
    print "body:"
    print body
    print "outdir"
    print outdir
    check_between(body,outdir)

