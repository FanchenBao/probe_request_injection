#!/bin/bash

# NOTE: Before running this script, making sure the regulatory database has
# already been modified either manually or via modify_regdb.py

MAX_RETRY=10

# Run the entire txpower modification in a separate shell because we need to
# set up `sudo su`.
tmux new -s mod_txpower -d
tmux send-keys -t mod_txpower 'cd $HOME/probe_request_injection/mod_txpower' Enter
tmux send-keys -t mod_txpower 'sudo su' Enter
tmux send-keys -t mod_txpower './apply_modified_regdb.sh' Enter

# Check when to reboot
ATTEMPT=0
while [ "$ATTEMPT" -lt "$MAX_RETRY" ]; do
    tmux capture-pane -t mod_txpower
    NUM_SUCCESS=$(tmux show-buffer | grep -c "CRDA install successful")
    if [ "$NUM_SUCCESS" -eq 1 ]; then
        echo "Modify txpower completed."
        break
    fi
    echo "Not completed yet..."
    sleep 5
    ATTEMPT=$((ATTEMPT + 1))
done
tmux kill-sess -t mod_txpower
if [ "$ATTEMPT" -eq "$MAX_RETRY" ]; then echo "Too many failures!"; fi
echo "Reboot"
sudo reboot