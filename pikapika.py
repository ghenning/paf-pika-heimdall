import pika
import subprocess
import os
import sys
import time

def printit(msg):
    print msg
    sys.stdout.flush()

def on_message(connection, channel, method_frame, header_frame, body,opts):
    printit( "Received file: {}".format(body))
    channel.basic_ack(delivery_tag=method_frame.delivery_tag)
    connection.close()
    
    filename=body
    gpu="0"
    outdir = "/output/{}".format(filename.split("/")[2]) # full path since we're mounting beegfs to beegfs
    try:
        os.mkdir(outdir)
    except OSError as error:
        printit( error)

    printit( "Calling Heimdall...")
    try:
        pass
        #subprocess.check_call(["/heimdall/Applications/heimdall", "-f", filename, "-gpu_id", gpu, "-dm", "0.0", "2000.0",
        #                 "-detect_thresh", "7.0", "-output_dir", outdir])
    except Exception as error:
        connection,channel = connect(opts)
        channel.basic_publish(exchange='',
                              routing_key='paf-heimdall-fail',
                              body="{}, {}".format(filename,str(error)),
                              properties=pika.BasicProperties(delivery_mode = 2,))
        printit( "Heimdall failed.")
        connection.close()
    else:
        connection,channel = connect(opts)
        channel.basic_publish(exchange='',
                              routing_key='paf-heimdall-success',
                              body=filename,
                              properties=pika.BasicProperties(delivery_mode = 2,))
        printit( "Heimdall done.")
        connection.close()
        
def connect(opts):
    url = "amqp://{opts.user}:{opts.pw}@{opts.host}:{opts.port}/%2F".format(opts=opts)
    #parameters = pika.URLParameters('amqp://guest:guest@134.104.70.90:5672/%2F')
    parameters = pika.URLParameters(url)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare("paf-heimdall-input", durable=True)
    channel.queue_declare("paf-heimdall-success", durable=True)
    channel.queue_declare("paf-heimdall-fail", durable=True)
    return connection, channel

def main(opts):
    while True:
        connection,channel = connect(opts)
        method_frame, header_frame, body = channel.basic_get('paf-heimdall-input')
        if method_frame:
            on_message(connection, channel, method_frame, header_frame, body,opts)
        else:
            print time.strftime("%c"),'No message returned, sleeping 30 seconds'
            time.sleep(30)

if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-H","--host", dest='host',default='134.104.70.91')
    parser.add_option("-p","--port", dest='port',default='5672')
    parser.add_option("-u","--user", dest='user',default='guest')
    parser.add_option("-w","--password",dest='pw',default='guest')
    (opts,args) = parser.parse_args()
    main(opts)

''' optparse!!!

rabbitMQ/pikaURL pw username host port (and default)
queue names
heimdall xtra args: 
fix gpu=0 !!!
kubectl get all
kubectl describe service rabbitmq
kubectl get services
'''
