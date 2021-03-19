import pika
import glob
import os
import pika_process as PP

# find filterbanks in PATH
def find_phil(PATH):
    dads = []
    for dirpath,dirnames,filenames in os.walk(PATH):
        for f in filenames:
            ff = os.path.join(dirpath,f)
            if os.path.splitext(ff)[-1] == '.fil':
                dads.append(ff)
    return dads


def main(producer, path):
    # old
    #thepath = os.path.join(path,"*_8bit.fil")
    #thepath = os.path.join(opts.path,"*/","*_8bit.fil") # dir with subdirs
    #thepath = os.path.join(opts.path,"2018-04*/","*_8bit.fil") # April run dirs
    ### this is for the old system/structure
    ### make something source-by-source basis like is done in convert_dada_fil.py
    #thepath = os.path.join(opts.path,"J1419*/","*_8bit.fil") # specific dirs
    #thepath = os.path.join(opts.path,"*_8bit.fil") # hi, I'm a comment

    ### find (glob) all filterbanks for a specific source and publish
    #fils = []
    #for dirpath,dirnames,filenames in os.walk(opts.path):
    #    for f in filenames:
    #        ff = os.path.join(dirpath,f)
    #        if os.path.splitext(ff)[-1] == '.fil':
    #            fils.append(ff)

    ### find all filterbanks for a specific source
    bigdir = '/beegfsEDD/PAF/PAF/SEARCH'
    Source = glob.glob(os.path.join(bigdir,"*"+opts.path))
    #for d in Source:
    #    D = find_phil(d)
    #    producer.publish(D)
    ### NEED TO SPLIT 2020 SUMMER AND WINTER DATA! ###
    # here you can set your restrictions on which data to publish to rabbit
    for d in Source:
        e = d.split(os.sep)[-1]
        #if "2020-12" in e: ### find the winter data
        if not "2020-12" in e: ### find the summer data
            D = find_phil(d)
            producer.publish(D)

    #old crap
    #thepath = os.path.join(opts.path,"2018-09-01_233441/B0609+37_180902_5_2/","*.fil") # test with concatenated PAF data
    #thepath = os.path.join(opts.path,"*.fil") # test with concatenated PAF data

    #do shit with glob results
    #producer.publish(glob.glob(thepath))

    #producer.publish(fils)

if __name__=="__main__":
    from optparse import OptionParser
    parser = OptionParser()
    PP.add_pika_producer_opts(parser)
    #parser.add_option("","--path",dest='path',help="Directory containing filterbank files",type=str,default="")
    #(opts,args) = parser.parse_args()
    #if opts.path == "":
    #    raise Exception("Expected --path argument")
    parser.add_option("","--source",dest='path',help="Name of source",type=str,default="")
    (opts,args) = parser.parse_args()
    if opts.path == "":
        raise Exception("Expected --source argument")
    producer = PP.pika_producer_from_opts(opts)
    main(producer, opts.path)

