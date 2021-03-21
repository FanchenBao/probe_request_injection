#!/bin/bash

main() {
  if [[ $INTERFACE == "" || $CHANNEL == "" ]]; then
      print_usage
      exit 1
  fi

  # Set target interface to monitor mode and emitting on channel 10
  CUR_MODE=$(iwconfig $INTERFACE | grep -Po "(?<=Mode:)\w+(?=\s)")
  if [[ $CUR_MODE != "Monitor" ]]; then
    echo "Change $INTERFACE from $CUR_MODE to Monitor"
    sudo ifconfig $INTERFACE down && sudo iwconfig $INTERFACE mode monitor && sudo ifconfig $INTERFACE up
  fi
  sudo iwconfig $INTERFACE channel $CHANNEL

  # Perform probe request injection in a tmux pane.
  tmux new -s emit -d
  tmux send-keys -t emit 'cd $HOME/probe_request_injection' Enter
  tmux send-keys -t emit 'sudo su' Enter
  tmux send-keys -t emit 'source venv/bin/activate' Enter
  tmux send-keys -t emit "python3 emit/emit_probe_request.py --interface $INTERFACE --interval $INTERVAL --mac $MAC" Enter
}


# DEFAULTS
INTERFACE=""
CHANNEL=""
INTERVAL="0.05"
MAC="''"  # default is an empty string literal

print_usage() {
  printf "%s\n" "Usage: emit.sh [-i wifi_interface] [-c channel] [--interval interval] [--mac mac_prefix]"
  printf "%s\t%s\n" "-i" "WiFi device interface in monitor mode. Type \"iwconfig\" to locate the target interface. Required." \
    "-c" "The channel on which probe request is injected. Required." \
    "--interval" "The interval in seconds between two consecutive probe request packets. Optional. Default to 0.05" \
    "--mac" "The MAC address prefix. See emit_probe_request.py for details. Default to empty string"
}

# Parse options and flags
while [[ "$#" -gt 0 ]]; do
  case "$1" in
    -i)  # wifi device interface that is in monitor mode
      if [[ "$2" != "" ]]; then
        INTERFACE="$2"
        shift 1
      else # -i must be followed by a second argument
        print_usage
        exit 1
      fi
      shift 1
      ;;
    -c)  # Channel
      if [[ "$2" != "" ]]; then
        CHANNEL="$2"
        shift 1
      else # -i must be followed by a second argument
        print_usage
        exit 1
      fi
      shift 1
      ;;
    --interval)  # gap duration between two consecutive probe request packets
      if [[ "$2" != "" ]]; then
        INTERVAL="$2"
        shift 1
      fi
      shift 1
      ;;
    --mac)  # MAC address prefix
      if [[ "$2" != "" ]]; then
        MAC="$2"
        shift 1
      fi
      shift 1
      ;;
    *) # unsupported flags
      print_usage
      exit 1
      ;;
  esac
done


main