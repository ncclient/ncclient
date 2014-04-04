#!/usr/bin/env python

from ncclient import manager


def connect(host, port, user, password, source):
    conn = manager.connect(host=host,
            port=port,
            username=user,
            password=password,
            timeout=10,
            device_params = {'name':'junos'},
            hostkey_verify=False)

    result_xml = conn.get_configuration(format='xml')

    # xpath starts-with
    ge_configs = result_xml.xpath('configuration/interfaces/interface/name[starts-with(text(), "ge-")]')
    for i in ge_configs:
        print i.tag, i.text

    # xpath re:match
    ge_configs = result_xml.xpath('configuration/interfaces/interface/name[re:match(text(), "ge")]')
    for i in ge_configs:
        print i.tag, i.text

    # xpath contains
    ge_configs = result_xml.xpath('configuration/interfaces/interface/name[contains(text(), "ge-")]')
    for i in ge_configs:
        print i.tag, i.text

    # xpath match on text
    ge_configs = result_xml.xpath('configuration/interfaces/interface/name[text()="ge-0/0/0"]')
    for i in ge_configs:
        print i.tag, i.text

    # xpath match on text - alternative (wildcards not permitted)
    ge_configs = result_xml.xpath('configuration/interfaces/interface[name="ge-0/0/0"]')
    for i in ge_configs:
        print i.xpath('name')[0].tag, i.xpath('name')[0].text


if __name__ == '__main__':
    connect('router', 830, 'netconf', 'juniper!', 'candidate')
