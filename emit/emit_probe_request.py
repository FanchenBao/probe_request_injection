from scapy.all import sendp, Dot11, RadioTap, RandMAC
from datetime import datetime
import logging
from argparse import ArgumentParser, RawDescriptionHelpFormatter
import re
import sys

logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
logger.setLevel(logging.DEBUG)


def get_argument_parser() -> ArgumentParser:
    """Set up a parser to parse command line arguments.

    :return: A fresh, unused, ArgumentParser.
    """
    parser = ArgumentParser(
        description='''
        This script is used to create simple mock probe request packets and
        emit them forever using the Scapy library.

        To generate mock probe request with current timestamp as its MAC
        address, emit it on wlan1, and with 1 second interval between emission,
        run:
        
        sudo su
        source venv/bin/activate
        python3 emit_probe_request.py --interface wlan1 --interval 1

        To emit probe request with a custom MAC address prefix, run:

        sudo su
        source venv/bin/activate
        python3 emit_probe_request.py --interface wlan1 --interval 1 --mac 11:22
        ''',
        formatter_class=RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        '--interface',
        dest='interface',
        type=str,
        required=True,
        help='''
        REQUIRED. The wireless interface where probe request will be emitted.
        ''',
    )
    parser.add_argument(
        '--interval',
        dest='interval',
        type=float,
        required=False,
        default=0.05,
        help='''
        OPTIONAL. The gap duration (in seconds) between two consecutive probe
        request packets. If set to 0, the wireless interface emits probe
        requests at its maximum capacity. The actual gap duration might be
        different from the set value as the WiFi chip approaches its physical
        limit. Default to 0.05 s.
        ''',
    )
    parser.add_argument(
        '--mac',
        dest='mac',
        type=str,
        required=False,
        default='',
        help='''
        OPTIONAL. The MAC address to use in the mock probe request. If
        speficied, all mock probe requests' MAC address will be prefixed by
        this argument. The remaining part of the MAC address will be random.
        If this argument contains the full length MAC address, all mock probe
        requests will have the same MAC address. This argument must follow the
        rule for MAC address, i.e. pairs of HEX decimals (lower case) separated
        by colons (e.g. 10:2a:df) and maximum six pairs of HEX decimals. If no
        MAC address is specified, the current timestamp (hour and minute) will
        be used as the prefix of the MAC address. For example, if the probe
        request is emitted within the minute of 15:31 local time, the MAC
        address will be "15:31:00:1a:2b:3c" where the first two pairs reflect
        the current timestamp, the third pair is "00" by design, and the last
        three pairs are randomly generated.
        ''',
    )
    return parser


if __name__ == '__main__':
    # Parse command line arguments
    parser: ArgumentParser = get_argument_parser()
    args = parser.parse_args()
    
    # check input mac prefix validity
    pattern: str = r'^((\d|[a-f]){2}:){1,5}(\d|[a-f]){2}$'
    if args.mac and not re.match(pattern, args.mac):
        logger.error(f'{args.mac} is an invalid MAC address prefix.')
        sys.exit(1)
    
    logger.info('Press CTRL+C to Abort')
    # Send mock probe request
    mac_pre = args.mac if args.mac else datetime.now().strftime('%H:%M') + ':00'
    sendp(RadioTap()/
        Dot11(
            type=0,
            subtype=4,
            addr1="ff:ff:ff:ff:ff:ff",
            addr2=RandMAC(mac_pre),
            addr3="ff:ff:ff:ff:ff:ff",
        ),
        iface=args.interface,
        loop=1,
        inter=args.interval,
    )
