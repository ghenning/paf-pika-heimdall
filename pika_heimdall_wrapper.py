import pika
import subprocess
import os
import sys
import time
import signal
import pika_process as PP
import thechecker

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
    if thechecker.check_between(body,outdir):
        return
    try:
        os.mkdir(outdir)
    except OSError as error:
        printit(error)

    printit( "Calling Heimdall...")
    subprocess.check_call(["/heimdall/Applications/heimdall", "-f", filename,
                           "-gpu_id", gpu, "-dm", str(opts.lodm), str(opts.hidm),
                           "-detect_thresh", str(opts.thresh), "-output_dir", outdir])
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
