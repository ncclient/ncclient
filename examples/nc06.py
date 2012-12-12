#! /usr/bin/env python
#
# Copyright 2012 Vaibhav Bajpai <contact@vaibhavbajpai.com>
# Copyright 2009 Shikhar Bhushan <shikhar@schmizz.net>
#
# Delete a list of existing users from the running configuration using
# edit-config; protect the transaction using a lock.
#
# $ ./nc06.py cook bob alice

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

template = """<config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
              <aaa xmlns="http://tail-f.com/ns/aaa/1.1">
              <authentication> <users> <user xc:operation="delete">
              <name>%s</name> </user></users></authentication></aaa></config>
           """
def connect(host, port, user, password, names):
    with manager.connect(
                          host=host, port=port,
                          username=user, password=password
                        ) as m:
        with m.locked(target='running'):
            for n in names:
                m.edit_config(target='running', config=template % n)

def parse_arguments():

    parser = argparse.ArgumentParser()
    parser.add_argument(
                        'hostname',
                        action='store',
                        help='hostname or IP address'
                       )
    parser.add_argument(
                        'names',
                        nargs='+',
                        action='store',
                        help='usernames of the users'
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
            results.username, results.password,
            results.names
           )
