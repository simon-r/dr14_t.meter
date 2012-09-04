#!/bin/sh

MAN_PREFIX="${PREFIX}/share/man"

for i in *.1; do
	section=`echo ${i}|sed 's/.*\([0-9]\).*/\1/'`
	
        #echo ${section}
	target="${MAN_PREFIX}/man${section}"
	
        # check if man directory exists	
	if ! test -d ${target}; then
	    mkdir -p ${target}
	fi
	echo "${i} --> ${target}"
	install -m644 ${i} ${target}
        gzip ${target}/${i}
done