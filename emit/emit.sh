#!/bin/bash

# Set wlan1 to monitor mode and emitting on channel 10
sudo ifconfig wlan1 down && sudo iwconfig wlan1 mode monitor && sudo ifconfig wlan1 up
sudo iwconfig wlan1 channel 10


tmux new -s emit -d
tmux send-keys -t emit 'cd $HOME/probe_request_injection' Enter
tmux send-keys -t emit 'sudo su' Enter
tmux send-keys -t emit 'source venv/bin/activate' Enter
tmux send-keys -t emit 'python3 emit/emit_probe_request.py' Enter
