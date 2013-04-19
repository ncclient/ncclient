#! /usr/bin/env python
#
# Copyright 2012 Vaibhav Bajpai <contact@vaibhavbajpai.com>
# Copyright 2009 Shikhar Bhushan <shikhar@schmizz.net>
#
# Create a new user to the running configuration using edit-config
# and the test-option provided by the :validate capability.
#
# $ ./nc04.py cook bob 42 42

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

def connect(host, port, user, password, name, uid, gid):
    snippet = """<config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
                 <aaa xmlns="http://tail-f.com/ns/aaa/1.1">
                 <authentication> <users> <user xc:operation="create">
                 <name>%s</name> <uid>%s</uid> <gid>%s</gid>
                 <password>*</password> <ssh_keydir/> <homedir/>
                 </user></users></authentication></aaa></config>
              """ % (name, uid, gid)
    with manager.connect(
                          host=host, port=port,
                          username=user, password=password
                        ) as m:
        assert(":validate" in m.server_capabilities)
        m.edit_config(
                      target='running', config=snippet,
                      test_option='test-then-set'
                     )

def parse_arguments():

    parser = argparse.ArgumentParser()
    parser.add_argument(
                        'hostname',
                        action='store',
                        help='hostname or IP address'
                       )
    parser.add_argument(
                        'name',
                        action='store',
                        help='username of the new user'
                       )
    parser.add_argument(
                        'uid',
                        action='store',
                        help='user id of the new user'
                       )
    parser.add_argument(
                        'gid',
                        action='store',
                        help='group id of the new user'
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
            results.name,
            results.uid, results.gid
           )
