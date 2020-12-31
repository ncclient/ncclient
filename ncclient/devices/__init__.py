# supported devices config, add new device (eg: 'device name':'device label').
supported_devices_cfg = {'junos':'Juniper',
                         'csr':'Cisco CSR1000v',
                         'nexus':'Cisco Nexus',
                         'iosxr':'Cisco IOS XR',
                         'iosxe':'Cisco IOS XE',
                         'huawei':'Huawei',
                         'huaweiyang':'Huawei',
                         'alu':'Alcatel Lucent',
                         'h3c':'H3C',
                         'hpcomware':'HP Comware',
                         'sros':'Nokia SR OS',
                         'default':'Server or anything not in above'}

def get_supported_devices():
    return tuple(supported_devices_cfg.keys())

def get_supported_device_labels():
    return supported_devices_cfg

