#! /usr/bin/env python
#
# Copyright 2012 Vaibhav Bajpai <contact@vaibhavbajpai.com>
# Copyright 2009 Shikhar Bhushan <shikhar@schmizz.net>
#
# Retrieve a config portion selected by an XPATH expression from the
# configuration store passed on the command line using
# get-config and write the XML configs to files.
#
# $ ./nc03.py cook "aaa/authentication/users/user[name='schoenw']"
# $ ./nc03.py yuma "interfaces/interface[name='eth0']"

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

def connect(host, port, user, password, source, expression):
    with manager.connect(
                          host=host, port=port,
                          username=user, password=password
                        ) as m:
        assert(":xpath" in m.server_capabilities)
        c = m.get_config(source, filter=('xpath', expression)).data_xml
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
                        'expression',
                        action='store',
                        help='xpath expression'
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
    parser.add_argument(
                        '--source',
                        action='store',
                        default='running',
                        help='running/candidate/startup [default: running]',
                        dest='source',
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
            results.source, results.expression
           )
