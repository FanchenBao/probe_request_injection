#!/bin/bash

# exit when any command fails
set -e

# For details of what these commands do, see this answer
# https://askubuntu.com/a/1169997/1193746

DB_DIR=/home/pi/probe_request_injection/mod_txpower/wireless-regdb-master-2019-06-03/
CRDA_DIR=/home/pi/probe_request_injection/mod_txpower/crda-4.14/

# Create new regdb files and public keys
cd $DB_DIR \
    && make clean \
    && make \
    && echo "regdb make successful"
# Copy the regulatory databases to their intended destination
cp $DB_DIR/regulatory.db /lib/firmware/ \
    && cp $DB_DIR/regulatory.db.p7s /lib/firmware/ \
    && cp $DB_DIR/regulatory.bin /lib/crda/ \
    && echo "regulatory db deployed successful"

# Copy the public keys to their intended destination
cp $DB_DIR/*.pub.pem $CRDA_DIR/pubkeys/ \
    && cp /lib/crda/pubkeys/*@*pub.pem $CRDA_DIR/pubkeys/ \
    && echo "Copy public keys successful"
# Install crda
cd $CRDA_DIR \
    && make clean \
    && make \
    && make install \
    && echo "CRDA install successful"