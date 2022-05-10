import configparser
import argparse
import logging
import os.path
from pathlib import Path

def arg_parse(args_array):
    """
    Creates/sets up argparser instance
    """
    parser = argparse.ArgumentParser(description=""" Jira Reporting Automator""",
                                     formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('-c', '--config', dest='config_file', default="config.ini",
                        help='parameters configuration file')
    parser.add_argument('-m', '--mode', dest='mode', help='Script mode',
                        choices=['add', 'remove', 't'], required=True)

    parser.add_argument("--dry_run", dest="dry_run", action="store_true", default=False,
                        help="Stop script just before applying changes on JIRA.")

    parser.add_argument('-f', '--file', dest='input_file',
                        help='File with data in CSV format.', required=True)
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument("-d", "--debug", dest='debug', action="store_true",
                       help='Debug mode (includes verbose mode)', default=False)
    group.add_argument('-v', '--verbose', dest='verbose', action="store_true",
                       help='Verbose mode', default=False)

    return parser.parse_args(args_array)


def get_logger(args):
    format = '%(asctime)s\t%(levelname)s\t%(message)s'
    logging.basicConfig(format=format)
    logger = logging.getLogger()

    logger.setLevel(logging.WARNING)
    if args.verbose:
        logger.setLevel(logging.INFO)
    if args.debug:
        logger.setLevel(logging.DEBUG)

    logger.debug("Args: %s", repr(args))
    return logger


def read_config(config_file_name):
    config = configparser.ConfigParser()
    config.read(config_file_name)
    return config


def split_path(file_path):
    path = os.path.realpath(file_path)
    o_path, o_name = os.path.split(path)

    return o_path, o_name


def get_out_files_name(input_file_path):
    path, file = split_path(input_file_path)

    ok_file_path = os.path.join(path, "out_%s.csv" % file)
    err_file_path = os.path.join(path, "err_%s.csv" % file)

    return ok_file_path, err_file_path


def is_file_already_processed(input_file_path):
    ok_file, err_file = get_out_files_name(input_file_path)

    if os.path.exists(ok_file) or os.path.exists(err_file):
        return True
    return False