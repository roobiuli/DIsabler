#!/bin/bash
POSITION=`cat test.txt | grep -in "make_resolv_conf(){" | cut -d":" -f1`
STARTERPOSITION=$POSITION
POWERPOSITION=$POSITION



while [[ `echo $starter | cut -c 1` != "}" ]]
do
POWERPOSITION=$((POWERPOSITION + 1))
starter=`cat test.txt | sed -e "$POWERPOSITION!d"`
done


###
RPOS=$((STARTERPOSITION + 1))

for range in {$RPOS .. $POWERPOSITION}
do
print "$range"
done