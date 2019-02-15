import pika
import glob
import os
import pika_process as PP

def main(producer, path):
    #thepath = os.path.join(path,"*_8bit.fil")
    #thepath = os.path.join(opts.path,"*/","*_8bit.fil") # dir with subdirs
    #thepath = os.path.join(opts.path,"2018-04*/","*_8bit.fil") # April run dirs
    #thepath = os.path.join(opts.path,"2018-09-01_233441/B0609+37_180902_5_2/","*.fil") # test with concatenated PAF data
    thepath = os.path.join(opts.path,"*.fil") # test with concatenated PAF data

    #do shit with glob results
    producer.publish(glob.glob(thepath))

if __name__=="__main__":
    from optparse import OptionParser
    parser = OptionParser()
    PP.add_pika_producer_opts(parser)
    parser.add_option("","--path",dest='path',help="Directory containing filterbank files",type=str,default="")
    (opts,args) = parser.parse_args()
    if opts.path == "":
        raise Exception("Expected --path argument")
    producer = PP.pika_producer_from_opts(opts)
    main(producer, opts.path)

