import pika
import glob
import os

def connect(opts):
    url = "amqp://{opts.user}:{opts.pw}@{opts.host}:{opts.port}/%2F".format(opts=opts)
    #parameters = pika.URLParameters('amqp://guest:guest@134.104.70.90:5672/%2F')
    parameters = pika.URLParameters(url)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare("paf-heimdall-input", durable=True)
    return connection, channel

def main(opts):
    thepath = os.path.join(opts.path,"*_8bit.fil")
    #thepath = os.path.join(opts.path,"*/","*_8bit.fil") # dir with subdirs
    files = glob.glob(thepath)
    #do shit with glob results
    connection,channel = connect(opts)
    for fname in files:
        channel.basic_publish(exchange='', routing_key='paf-heimdall-input', 
                body=fname, properties=pika.BasicProperties(delivery_mode = 2,))

if __name__=="__main__":
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-H","--host", dest='host',default='134.104.70.91')
    parser.add_option("-p","--port", dest='port',default='5672')
    parser.add_option("-u","--user", dest='user',default='guest')
    parser.add_option("-w","--password",dest='pw',default='guest')
    parser.add_option("-d","--path",dest='path')
    (opts,args) = parser.parse_args()
    main(opts)

