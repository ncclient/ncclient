#! /usr/bin/env python
#
# Copyright 2012 Vaibhav Bajpai <contact@vaibhavbajpai.com>
# Copyright 2009 Shikhar Bhushan <shikhar@schmizz.net>
#
# Retreive configuration from the candidate datastore after performing
# a discard-changes on it.
#
# $ ./nc08.py cook

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
        assert(":candidate" in m.server_capabilities)
        with m.locked(target='candidate'):
            m.discard_changes()
            c = m.get_config('candidate').data_xml
            with open("%s.xml" % host, 'w') as f:
                f.write(c)

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
                        dest='password',
                        help='password'
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
