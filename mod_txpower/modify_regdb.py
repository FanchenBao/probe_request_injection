from pathlib import Path
import re
import subprocess
import shlex
import os
import logging
from argparse import ArgumentParser, RawDescriptionHelpFormatter
import sys

logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
logger.setLevel(logging.DEBUG)

DB_PATH = Path(__file__).absolute().parent.joinpath('wireless-regdb-master-2019-06-03/db.txt')


def get_argument_parser() -> ArgumentParser:
    """Set up a parser to parse command line arguments.

    :return: A fresh, unused, ArgumentParser.
    """
    parser = ArgumentParser(
        description='''
        Change the max txpower of a given country code on the wireless-regdb
        database file under 2.4 GHz (the database must be in this location:
        ./wireless-regdb-master-2019-06-03/db.txt). The script logs the max
        txpower before and after it is modified. Or, if the power argument is
        a negative value, only the before value is logged. The script exit with
        the current txpower in the regulatory database. So exit code should NOT
        be used in their traditional meaning to check whether the script has
        run successfully. If the script fails, it exits with -1. If it succeeds,
        it exits with the txpower, which can be captured by $? right afterwards.

        For example, to change the max txpower associated with Great Britain
        under 2.4 GHz in the wireless-regdb to 20 dBm:
        
        python3 modify_regdb.py --country GB --power 20

        To check the current max txpower associated with USA without modifying
        it in the regdb:

        python3 modify_regdb.py --country US --power -1

        To capture the current max txpower without modification:

        python3 modify_regdb.py --country US --power -1
        echo $?
        ''',
        formatter_class=RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        '--country',
        dest='country',
        type=str,
        required=True,
        help='REQUIRED. The country code (two letters, case insensitive).',
    )
    parser.add_argument(
        '--power',
        dest='power',
        type=str,
        required=True,
        help='''
        REQUIRED. The desired power to change to. We will swap the power value
        associated with the country code to this new value. If a negative value
        is provided, the database is not modified.
        ''',
    )
    return parser


def modify_regdb(country: str, power: int) -> int:
    """Modify the database that contains the max txpower of each country.

    The process is to swap the power value currently in the db file associated
    with the country input with the new power input.

    :param country: A two letter country code of interest.
    :param power: The new power to set for the provided country.
    :return: Either the previous max txpower or the modified max txpower.
    """
    with open(DB_PATH, 'r') as f_obj:
        db = f_obj.read()

    pattern = r'({}.+\n.+\()(\d+)'.format(country)
    match = re.search(pattern, db)
    logger.info(f'Before change: {country} -> {match.group(2)}')

    if power >= 0:
        # Swap old power with new
        new_db = re.sub(pattern, match.group(1) + str(power), db)
        # Save updated file
        with open(DB_PATH, 'w') as f_obj:
            f_obj.write(new_db)
        # Sanity check
        with open(DB_PATH, 'r') as f_obj:
            db_ = f_obj.read()
        match_ = re.search(pattern, db_)
        logger.info(f'After change: {country} -> {match_.group(2)}')
        return int(match_.group(2))  # modified txpower
    return int(match.group(2))  # previous txpower


if __name__ == '__main__':
    # Parse command line arguments
    parser: ArgumentParser = get_argument_parser()
    args = parser.parse_args()
    
    try:
        txpower = modify_regdb(args.country.upper(), int(args.power))
    except Exception:
        logger.exception('Cannot modify regulatory database.')
        sys.exit(-1)
    sys.exit(txpower)
