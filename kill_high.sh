#!/bin/bash

THRESHOLD=90

ps -eLo pid,tid,%cpu,comm --sort=-%cpu | awk -v threshold="$THRESHOLD" '$3 > threshold {print $2}' | while read tid; do
	echo "killing thread $tid with high CPU usage"
	kill -9 "$tid"
done
