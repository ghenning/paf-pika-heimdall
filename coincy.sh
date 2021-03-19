#!/bin/bash -l

# run coincidencer on source candidates

# path to coincidencer
C="/heimdall/Applications/coincidencer"
# path to results directory
maindir="/beegfsEDD/PAF/PAF/RESULTS/"
pwd
cd "$maindir"
pwd
# check if there was a source name input, then loop over all
# result directories of the source
# this is done from a Heimdall container, so chown/chmod 
# to pulsar group is needed
# tailor this to your needs (specific source dirs etc...)
if [ -z $1 ]; then
	echo "missing source name input"
else
	for f in $1*; do
		if [ -d "$f" ]; then
			cd "$f"
			echo "$f"
			echo "running coincidencer on $f"
			"$C" -n 32 *.cand
			#chown 50000:50000 *all.cand
			chown 4875:6850 *all.cand
			chmod g=u *all.cand
			echo "coincidencer done"
			cd ..
		fi
done
fi
