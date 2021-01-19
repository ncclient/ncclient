#!/usr/bin/env python
#
# For Nokia SR OS > 20.10, support for issuing a subset of CLI commands
# (e.g. 'show', 'admin', 'clear', 'ping', etc..) over NETCONF RPCs is
# achieved by the use of the <md-cli-raw-command> YANG 1.1 action

import logging
import sys

from ncclient import manager
from ncclient.operations.rpc import RPCError

_NS_MAP = {
    'nc': 'urn:ietf:params:xml:ns:netconf:base:1.0',
    'nokia-oper': 'urn:nokia.com:sros:ns:yang:sr:oper-global'
}

def connect(host, port, user, password):
    m = manager.connect(host=host, port=port,
            username=user, password=password,
            device_params={'name': 'sros'},
            hostkey_verify=False)

    ## Issue 'show card' and display the raw XML output
    result = m.md_cli_raw_command('show card')
    logging.info(result)

    ## Issue 'show port' from MD-CLI context and emit only
    ## the returned command contents
    result = m.md_cli_raw_command('show port')
    output = result.xpath(
            '/nc:rpc-reply/nokia-oper:results' \
            '/nokia-oper:md-cli-output-block',
            namespaces=_NS_MAP)[0].text
    logging.info(output)

    ## Issue 'show version' from Classic CLI context and emit
    ## only the returned command contents
    result = m.md_cli_raw_command('//show version')
    output = result.xpath(
            '/nc:rpc-reply/nokia-oper:results' \
            '/nokia-oper:md-cli-output-block',
            namespaces=_NS_MAP)[0].text
    logging.info(output)

    ## Issue 'ping' from MD-CLI context and emit only the
    ## returned command contents
    result = m.md_cli_raw_command(
            'ping 127.0.0.1 router-instance "Base" count 3')
    output = result.xpath(
            '/nc:rpc-reply/nokia-oper:results' \
            '/nokia-oper:md-cli-output-block',
            namespaces=_NS_MAP)[0].text
    logging.info(output)

    ## Issue an admin command that returns only NETCONF <ok/> or
    ## <rpc-error/>
    result = m.md_cli_raw_command('admin save')
    try:
        if len(result.xpath('/nc:rpc-reply/nc:ok', namespaces=_NS_MAP)) > 0:
            logging.info('Admin save successful')
        else:
            logging.info('Admin save unsuccessful')

    except RPCError as err:
        logging.info('Error: %s' % err.message.strip())


    ## Issue an unsupported command and handle the RPC error gracefully
    try:
        result = m.md_cli_raw_command('configure')
        if len(result.xpath('/nc:rpc-reply/nc:ok', namespaces=_NS_MAP)) > 0:
            logging.info('Command successful')
        else:
            logging.info('Command unsuccessful')

    except RPCError as err:
        logging.info('Error: %s' % err.message.strip())

    m.close_session()

if __name__ == '__main__':
    LOG_FORMAT = '%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s'
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=LOG_FORMAT)

    try:
        connect(sys.argv[1], '830', 'admin', 'admin')

    except IndexError:
        logging.error('Must supply a valid hostname or IP address')


