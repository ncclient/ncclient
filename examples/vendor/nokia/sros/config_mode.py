import logging
import sys
import threading
import time
from ncclient import manager

# Device connection details
DEVICE_HOST = 'localhost'
DEVICE_PORT = 830
DEVICE_USER = 'admin'
DEVICE_PASS = 'admin'

# Configuration payload template for SNMP community string
EDIT_CONFIG_PAYLOAD = """
<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
    <configure xmlns="urn:nokia.com:sros:ns:yang:sr:conf">
        <system>
            <security>
                <snmp>
                    <community>
                        <community-string>TestCommunity-{}</community-string>
                        <access-permissions>r</access-permissions>
                        <version>v2c</version>
                    </community>
                </snmp>
            </security>
        </system>
    </configure>
</config>
"""


def create_ncclient_session(host, port, username, password, config_mode=None):
    """
    Creates and returns an ncclient manager session for connecting to the Nokia SR OS device.

    :param host: Hostname or IP of the Nokia device
    :param port: NETCONF port
    :param username: Username for device authentication
    :param password: Password for device authentication
    :param config_mode: 'private' to use private candidate mode, None for default mode
    :return: NETCONF manager session
    """
    device_params = {'name': 'sros'}
    if config_mode:
        device_params['config_mode'] = config_mode

    return manager.connect(
        host=host,
        port=port,
        username=username,
        password=password,
        hostkey_verify=False,
        device_params=device_params
    )


def configure_and_commit(session_id, config_mode=None):
    """
    Creates a NETCONF session, edits the configuration, and commits the changes.

    :param session_id: Unique session identifier for logging
    :param config_mode: 'private' for private candidate mode, None for default mode
    """
    try:
        with create_ncclient_session(DEVICE_HOST, DEVICE_PORT, DEVICE_USER, DEVICE_PASS, config_mode=config_mode) as nc_session:
            logging.info(f"Session {session_id} started with config_mode: {config_mode or 'default'}")

            # Edit the device configuration using the payload
            edit_payload = EDIT_CONFIG_PAYLOAD.format(session_id)
            nc_session.edit_config(target='candidate', config=edit_payload)
            logging.info(f"Session {session_id} successfully edited the configuration.")

            # Commit the changes to the device
            nc_session.commit(comment=f"Session {session_id} commit in {config_mode or 'default'} mode")
            logging.info(f"Session {session_id} committed successfully in {config_mode or 'default'} mode.")

    except Exception as e:
        logging.error(f"Session {session_id} encountered an error: {e}")


def run_concurrent_sessions(session_ids, config_mode=None):
    """
    Runs multiple NETCONF sessions concurrently.

    :param session_ids: List of session IDs to identify different threads
    :param config_mode: 'private' to use private candidate mode, None for default mode
    """
    threads = []
    for session_id in session_ids:
        thread = threading.Thread(target=configure_and_commit, args=(session_id, config_mode))
        threads.append(thread)
        thread.start()

    # Ensure all threads finish execution
    for thread in threads:
        thread.join()


def main():
    LOG_FORMAT = '%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s'
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=LOG_FORMAT)

    logging.info("Starting test with concurrent sessions in default mode (expecting conflicts)...")

    # Run test with concurrent sessions in default mode
    run_concurrent_sessions([1, 2, 3, 4, 5])

    logging.info("Now testing with concurrent sessions in private mode (no conflicts expected)...")

    # Run test with concurrent sessions in private candidate mode
    run_concurrent_sessions([6, 7, 8, 9], config_mode='private')

    logging.info("Test completed.")


if __name__ == '__main__':
    main()
