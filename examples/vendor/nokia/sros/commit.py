import logging
import sys

from ncclient import manager

# Global constants
DEVICE_HOST = 'localhost'
DEVICE_PORT = 830
DEVICE_USER = 'admin'
DEVICE_PASS = 'admin'

EDIT_CONFIG_PAYLOAD = """
<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:alu="urn:ietf:params:xml:ns:netconf:base:1.0">
    <configure xmlns="urn:nokia.com:sros:ns:yang:sr:conf">
        <system>
            <security>
                <snmp>
                    <community alu:operation="replace">
                        <community-string>Sample Community</community-string>
                        <access-permissions>r</access-permissions>
                        <version>v2c</version>
                    </community>
                </snmp>
            </security>
        </system>
    </configure>
</config>
"""


def create_session(host, port, username, password):
    """Creates and returns an ncclient manager session."""
    return manager.connect(
        host=host,
        port=port,
        username=username,
        password=password,
        hostkey_verify=False,
        device_params={'name': 'sros'}
    )


def edit_config(m, config_payload):
    """Edits the configuration with the given payload."""
    m.edit_config(target='candidate', config=config_payload)


def commit_changes(m, comment=''):
    """Commits changes with an optional comment."""
    response = m.commit(comment=comment)
    logging.info(response)


def main():
    LOG_FORMAT = '%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s'
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=LOG_FORMAT)

    try:
        with create_session(DEVICE_HOST, DEVICE_PORT, DEVICE_USER, DEVICE_PASS) as m:
            # Lock the configuration
            m.lock(target='candidate')

            # Edit the configuration
            edit_config(m, EDIT_CONFIG_PAYLOAD)

            # Commit the configuration
            commit_changes(m, comment='A sample commit comment goes here')

            # Unlock the configuration
            m.unlock(target='candidate')

    except Exception as e:
        logging.error(f"Encountered an error: {e}")


if __name__ == '__main__':
    main()
