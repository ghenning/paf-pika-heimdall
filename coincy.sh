#!/bin/bash -l

C="/heimdall/Applications/coincidencer"
maindir="/beegfsEDD/PAF/PAF/RESULTS/"
pwd
cd "$maindir"
pwd
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
