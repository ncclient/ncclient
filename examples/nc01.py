#! /usr/bin/env python
#
# Copyright 2012 Vaibhav Bajpai <contact@vaibhavbajpai.com>
# Copyright 2009 Shikhar Bhushan <shikhar@schmizz.net>
#
# Connect to the NETCONF server passed on the command line and
# display their capabilities. For brevity and clarity of the
# examples, we omit proper exception handling.
#
# $ ./nc01.py cook

import sys, os, warnings, logging, argparse
warnings.simplefilter("ignore", DeprecationWarning)
from ncclient import manager

LEVELS = {
           'debug':logging.DEBUG,
           'info':logging.INFO,
           'warning':logging.WARNING,
           'error':logging.ERROR,
           'critical':logging.CRITICAL,
         }

def connect(host, port, user, password):
    with manager.connect(
                          host=host, port=port,
                          username=user, password=password
                        ) as m:
        for c in m.server_capabilities:
            print c

def parse_arguments():

    parser = argparse.ArgumentParser()
    parser.add_argument(
                        'hostname',
                        action='store',
                        help='hostname or IP address'
                       )
    parser.add_argument(
                        '--port',
                        action='store',
                        default=830,
                        type=int,
                        dest='port',
                        help='''port number [default: 830]'''
                       )
    parser.add_argument(
                        '--logging',
                        action='store',
                        dest='level_name',
                        help='''debug/info/warning/error/critical
                                [default: critical]'''
                       )
    parser.add_argument(
                        '--username',
                        action='store',
                        dest='username',
                        default=os.getenv('USER'),
                        help='username [default: %s]'%(os.getenv('USER'))
                       )
    parser.add_argument(
                        '--password',
                        action='store',
                        help='password',
                        dest='password',
                       )
    results = parser.parse_args()
    return results

if __name__ == '__main__':

    def setlogging_level(level_name):
        level = LEVELS.get(level_name, logging.CRITICAL)
        logging.basicConfig(level=level)

    results = parse_arguments()
    setlogging_level(results.level_name)
    connect(
            results.hostname, results.port,
            results.username, results.password
           )
