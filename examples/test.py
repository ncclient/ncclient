from ncclient import manager

import logging
logging.basicConfig(level=logging.DEBUG)

with manager.connect('broccoli', 22, username='sbhushan') as m:
    with m.locked('candidate'):
        reply = m.copy_config(source='running', target='candidate')

print reply
