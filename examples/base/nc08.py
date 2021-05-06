#! /usr/bin/env python
#
# Configure an Interface: its description and make it active.
# XML payload created with lxml/etree instead of a template
# 
# $ ./nc08.py Paulo Seguel

import sys, os, warnings
warnings.simplefilter("ignore", DeprecationWarning)
import datetime
from ncclient import manager
from lxml import etree

current_time = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
 
# build xml
config_e = etree.Element("config")
configuration = etree.SubElement(config_e, "interface-configurations", nsmap = {None: 'http://cisco.com/ns/yang/Cisco-IOS-XR-ifmgr-cfg'})
interface_cfg = etree.SubElement(configuration, "interface-configuration")
active = etree.SubElement(interface_cfg, "active").text = 'act'
interface_name = etree.SubElement(interface_cfg, "interface-name").text = 'GigabitEthernet0/0/0/0'
description = etree.SubElement(interface_cfg, "description").text  = 'NETCONF configured - ' + current_time

def demo(host, user, password):
    with manager.connect(host=host, port=830, username=user, password=password,
                     hostkey_verify=False, device_params={'name':'default'},
                     look_for_keys=False, allow_agent=False) as m:
        with m.locked(target="candidate"):
            m.edit_config(config=config_e, default_operation="merge", target="candidate")
            m.commit()

if __name__ == '__main__':
    demo(sys.argv[1], sys.argv[2], sys.argv[3])

