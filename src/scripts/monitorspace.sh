#!/bin/sh

PIDFILE="/run/spaace/space.pid"
DISABLE_FILE="/run/space/monitor_pause"

while true; do
	if [ ! -f ${DISABLE_FILE} ]; then

	    if [ -f ${PIDFILE} ]; then
            pgrep --pidfile $PIDFILE 2> /dev/null
            DIED="$?"

            if [ ${DIED} -eq 1 ]; then
                rm ${PIDFILE}
            fi
	    fi

        if [ ! -f ${PIDFILE} ]; then
            /etc/init.d/space silent
            sleep 2
        fi

	fi

	sleep 3
done
