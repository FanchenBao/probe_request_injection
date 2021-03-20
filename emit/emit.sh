#!/bin/bash

main() {
  if [[ $INTERFACE == "" || $CHANNEL == "" ]]; then
      print_usage
      exit 1
  fi

  # Set target interface to monitor mode and emitting on channel 10
  sudo ifconfig $INTERFACE down && sudo iwconfig $INTERFACE mode monitor && sudo ifconfig $INTERFACE up
  sudo iwconfig $INTERFACE channel $CHANNEL

  # Perform probe request injection in a tmux pane.
  tmux new -s emit -d
  tmux send-keys -t emit 'cd $HOME/probe_request_injection' Enter
  tmux send-keys -t emit 'sudo su' Enter
  tmux send-keys -t emit 'source venv/bin/activate' Enter
  tmux send-keys -t emit 'python3 emit/emit_probe_request.py' Enter
}


# DEFAULTS
INTERFACE=""
CHANNEL=""

print_usage() {
  printf "%s\n" "Usage: emit.sh [-i wifi_interface] [-c channel]"
  printf "%s\t%s\n" "-i" "WiFi device interface in monitor mode. Type \"iwconfig\" to locate the target interface. Required." \
    "-c" "The channel on which probe request is injected. Required."
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
    *) # unsupported flags
      print_usage
      exit 1
      ;;
  esac
done


main