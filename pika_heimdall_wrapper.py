import pika
import subprocess
import os
import sys
import time
import signal
import pika_process as PP
#import thechecker

def printit(msg):
    print msg
    sys.stdout.flush()

def on_message(body, opts):
    printit( "Received file: {}".format(body))
    filename=body
    gpu="0"
    #outdir = "/output/{}".format(filename.split("/")[2]) # full path since we're mounting beegfs to beegfs
    outdir = "/beegfs/heimpaf/processed/{}".format(filename.split("/")[-2]) # full path since we're mounting beegfs to beegfs
    # NB: the outdir thing might need some work to make it a bit cleaner/fancier
    # thechecker only works for the original naming convention, it's not the end of the world if we
    # end up re-running some stuff...
    #if thechecker.check_between(body,outdir):
        #return
    try:
        os.mkdir(outdir)
    except OSError as error:
        printit(error)

    printit( "Calling Heimdall...")
    subprocess.check_call(["/heimdall/Applications/heimdall", "-f", filename,
                           "-gpu_id", gpu, "-dm", str(opts.lodm), str(opts.hidm),
                           #"-zap_chans", str(330), str(400),
                           #"-zap_chans", str(425), str(440),
                           #"-zap_chans", str(470), str(495),
                           #"-zap_chans", str(500), str(512),
                           "-detect_thresh", str(opts.thresh), "-output_dir", outdir])
                           #"-zap_chans", str(330), str(512),
                           #"-detect_thresh", str(opts.thresh), "-output_dir", outdir,
                           #"-zap_chans", str(329), str(400), # to deal with the shitty lower half of band
                           #"-zap_chans", str(424), str(440), 
                           #"-zap_chans", str(469), str(495), 
                           #"-zap_chans", str(499), str(511)])
                           #"-detect_thresh", str(opts.thresh), "-output_dir", outdir])
                           #"-zap_chans", str(329), str(400), "-zap_chans", str(424), str(440), "-zap_chans", str(469), str(495),
                           #"-zap_chans", str(499), str(511)])
    subprocess.check_call(['chown','-R','50000:50000',str(outdir)])

if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser()
    PP.add_pika_process_opts(parser)
    parser.add_option("-d","--lowdm",dest='lodm',default=0.0)
    parser.add_option("-D","--highdm",dest='hidm',default=2000.0)
    parser.add_option("-T","--thresh",dest='thresh',default=7.0)
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
