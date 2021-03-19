# PAF processing

Congratulations! You've finished a gruelling observing run with the PAF, now what? You need to convert the data to filterbanks and search for single pulses!

This document will guide you on how to go from the PAF observational data to obtaining Heimdall single pulse candidates. For plotting/sifting of those candidates, check [*this out*](https://github.com/ghenning/PAFcode). That process is a bit too slow for the insane amount of candidates we get from the PAF, so an ML candidate classifier is being worked on [*here (TBA)*](https://github.com/shiningsurya)!

### Directory structure

Brief note on the directory structure. Recorded data goes to `/beegfsEDD/PAF/PAF/SEARCH/<timestamp>_<source>/BEAM<beam>/DATA/`, and the data are labeled as `<timestamp>.dada`. The search results directory is `/beegfsEDD/PAF/PAF/RESULTS/<source>_<timestamp>/`

## Converting data

The first step is to convert the data to a format that Heimdall understands. That is done with `convert_dada_fil.py`, which goes through all the PAF data directories of a source and converts them from `dada` to `fil`. `convert_dada_fil.py` uses `digifil`, which is a part of `dspsr`, so we need to whip up a Docker container. This can be done on any pacifix node with
```sh
docker run --rm -ti 
-v /beegfsEDD/PAF/PAF/SEARCH:/beegfsEDD/PAF/PAF/SEARCH 
-v /beegfsEDD/PAF/PAF/RESULTS:/beegfsEDD/PAF/PAF/RESULTS
-v /beegfsEDD/kubernetes/paf-pika-heimdall:/beegfsEDD/kubernetes/paf-pika-heimdall
mpifrpsr/dspsr bash
```
Let's say we observed the source *Papa_smurf*, then converting the data to filterbanks would be
```sh
python convert_dada_fil.py --source Papa_smurf
```
Because Heimdall cannot distinguish between beams 0 and 1, we need to add 1 to each beam number, so the beams go from 1 to 32 instead of 0 to 31. To do this simply run
```sh
python convert_dada_fil.py --sourcebeams Papa_smurf
```
To avoid re-converting old data, some timestamp checks in the `find_dad` and `find_phil` definitions of `convert_dada_fil.py` are required. Go nuts in adjusting this to your needs!

## Processing setup
Until further notice, the Kubernetes cluster on the pacifix machines is not in use. In that case we need to set up instances of RabbitMQ and Heimdall on each node that you want to use. If the Kubernetes cluster is magically revived, you can use the `yaml` files here to set up your Kubernetes nodes.
### Set up RabbitMQ server

ssh to the pacifix node in which you want to set up a RabbitMQ server and run
```sh
docker run -d --name rabbitmq-service -p 30001:15672 -p 31861:5672 rabbitmq:3.6-management
```
### Accessing the RabbitMQ web interface
Open a terminal and ssh to the MPI portal using port forwarding
```
ssh -D 50000 mpifr
```
Open a terminal and use it to open google chrome
```sh
google-chrome --user-data-dir="$HOME/proxy-profile" --proxy-server="socks5://localhost:50000"
```
(on macs you might need to write `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome` instead of just `google-chrome`). This should open up a fresh chrome instance. To access the RabbitMQ web interface type the following into the address bar
```sh
134.104.70.97:30001
```
where "97" refers to pacifix7, so change this number accordingly (e.g. 91 for pacifix1).

### Set up Heimdall instances

If this is set up without the use of a Kubernetes cluster, two Heimdall Docker containers are required on each intended node to use: A container that will perpetually run Heimdall, waiting for the RabbitMQ service to feed it paths to filterbanks, and a container that is used to feed Rabbit with filterbanks.

Let's first start with the Heimdall processing container. On the pacifix node you intend to use, we set up the container by pulling the MPIfR Heimdall image and link it to the RabbitMQ service by running
```sh
docker run -ti --name heimdall --link rabbitmq-service --entrypoint bash 
-v /beegfsEDD/PAF/PAF/SEARCH:/beegfsEDD/PAF/PAF/SEARCH 
-v /beegfsEDD/PAF/PAF/RESULTS:/beegfsEDD/PAF/PAF/RESULTS
-v /beegfsEDD/kubernetes/paf-pika-heimdall:/beegfsEDD/kubernetes/paf-pika-heimdall
mpifrpsr/heimdall
```

Now deattach from the container with `ctrl p + q` and copy the correct version of the Heimdall wrapper to the container from `beegfsEDD/kubernetes/paf-pika-heimdall` with
```sh
docker cp pika_heimdall_wrapper.py heimdall:/heimdall/Scripts/
```
Attach to the container again with `docker attach heimdall` and start Heimdall
```sh
cd /heimdall/Scripts/
python pika_heimdall_wrapper.py --input paf-heimdall-input --success paf-heimdall-success --fail paf-heimdall-fail
```
`pika_heimdall_wrapper.py` is a Heimdall wrapper that, once started, waits for filterbank inputs from Rabbit. You can set the low and high DM boundaries and the signal-to-noise threshold when starting the wrapper, or just change the defaults in the script. Additionally, you can change the channel zap ranges in the wrapper, or add it as an option if you feel up for it.

Deattach again with `ctrl p + q` and let's set up the feeder container. Setting up this container is pretty much the same as before.
```sh
docker run -ti --name heimdall-feeder --link rabbitmq-service --entrypoint bash
-v /beegfsEDD/PAF/PAF/SEARCH:/beegfsEDD/PAF/PAF/SEARCH 
-v /beegfsEDD/PAF/PAF/RESULTS:/beegfsEDD/PAF/PAF/RESULTS
-v /beegfsEDD/kubernetes/paf-pika-heimdall:/beegfsEDD/kubernetes/paf-pika-heimdall
mpifrpsr/heimdall
```
Deattach from the container (`ctrl p + q`) and copy the correct version of the data grabber to the container from `/beegfsEDD/kubernetes/paf-pika-heimdall` with
```sh
docker cp pika_get_data.py heimdall-feeder:/heimdall/Scripts/
```
Attach to the container again with `docker attach hemidall-feeder` and send the data to Rabbit
```sh
cd /heimdall/Scripts/
python pika_get_data.py -q paf-heimdall-input --source <source name>
```
`pika_get_data.py` searches the data directory for all filterbanks of the input source and sends the filterbank paths to Rabbit. You can change the timestamp constraint in order to avoid re-processing already processed data.

Heimdall writes out single pulse candidates that are saved in a source's corresponding results directory. Each candidate file contains candidates of a single beam over some time interval. To make more sense out of the candidates they need to be coincidenced using Heimdall's coincidencer. This can be done using `coincy.sh`, which loops through each result directory of a source and runs the coincidencer. Since the coincidencer is a part of Heimdall you'll need to run it from a Heimdall container. Luckily, we have such a container ready in `heimdall-feeder`. Simply re-attach to `heimdall-feeder` and run 
```sh
./coincy.sh <source name>
```
Heimdall candidate files are labeled as `<timestamp>_<beam number>.cand`, while the coincidenced candidate file is labeled `<timestamp>_all.cand`.

Once the Heimdall candidates have been concidenced, you can inspect them using [*this (OLD)*](https://github.com/ghenning/PAFcode) or [*this (work in progress)*](https://github.com/shiningsurya). 


