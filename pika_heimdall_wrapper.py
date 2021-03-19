import pika
import subprocess
import os
import sys
import time
import signal
import pika_process as PP
# old import for pre-2020 data
#import thechecker

def printit(msg):
    print msg
    sys.stdout.flush()

def on_message(body, opts):
    printit( "Received file: {}".format(body))
    filename=body
    gpu="0"
    #outdir = "/output/{}".format(filename.split("/")[2]) # full path since we're mounting beegfs to beegfs
    ###outdir = "/beegfs/heimpaf/processed/{}".format(filename.split("/")[-2]) # full path since we're mounting beegfs to beegfs
    # NB: the outdir thing might need some work to make it a bit cleaner/fancier
    # creating the name of the output directory
    outd_name = os.path.basename(filename).split('_BEAM_')[0]
    new_out = '/beegfsEDD/PAF/PAF/RESULTS/'
    outdir = os.path.join(new_out,outd_name)
    # old
    #if thechecker.check_between(body,outdir):
    #    return
    # thechecker only works for the original naming convention, it's not the end of the world if we
    # end up re-running some stuff...
    #if thechecker.check_between(body,outdir):
        #return
    # creating the output directory
    try:
        os.mkdir(outdir)
    except OSError as error:
        printit(error)

    # running Heimdall
    # manually set zap ranges here, or change the script to automate it
    printit( "Calling Heimdall...")
    subprocess.check_call(["/heimdall/Applications/heimdall", "-f", filename,
                           "-gpu_id", gpu, "-dm", str(opts.lodm), str(opts.hidm),
                           ### summer 2020 zaps
                           "-zap_chans", str(300), str(320),
                           "-zap_chans", str(350), str(420),
                           "-zap_chans", str(450), str(460),
                           "-zap_chans", str(490), str(500),
                           ### winter 2020 zaps
                           #"-zap_chans", str(165), str(340),
                           #"-zap_chans", str(345), str(355),
                           #"-zap_chans", str(380), str(390),
                           #"-zap_chans", str(400), str(410),
                           #"-zap_chans", str(435), str(455),
                           "-detect_thresh", str(opts.thresh), "-output_dir", outdir])
    #subprocess.check_call(['chown','-R','50000:50000',str(outdir)]) # old pulsar account
    # need to chown and chmod to pulsar group
    subprocess.check_call(['chown','-R','4875:6850',str(outdir)]) 
    subprocess.check_call(['chmod','-R','g=u',str(outdir)])

if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser()
    PP.add_pika_process_opts(parser)
    parser.add_option("-d","--lowdm",dest='lodm',default=0.0)
    parser.add_option("-D","--highdm",dest='hidm',default=2000.0)
    parser.add_option("-T","--thresh",dest='thresh',default=8.0)
    (opts,args) = parser.parse_args()
    processor = PP.pika_process_from_opts(opts)
    processor.process(lambda message: on_message(message, opts))

''' optparse!!!

rabbitMQ/pikaURL pw username host port (and default) DONE
queue names DONE
heimdall xtra args: DONE
atexit, at fail put file back to input queue
fix gpu=0 !!!
kubectl get all
kubectl describe service rabbitmq
kubectl get services
'''
