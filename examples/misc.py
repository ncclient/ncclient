#import logging
#logging.basicConfig(level=logging.DEBUG)

from ncclient import manager
from ncclient.operations import RPCError

m = manager.connect('broccoli', 22, username='sbhushan')

# add user
print 'Add user:',
config = """<config>
    <aaa xmlns="http://tail-f.com/ns/aaa/1.1">
	<authentication>
	    <users>
		<user>
		    <name>testtailf</name>
		    <uid>9099</uid>
		    <gid>1</gid>
		    <password>testtailf</password>
		    <ssh_keydir/>
		    <homedir/>
		</user>
	    </users>
	</authentication>
    </aaa>
</config>"""
try:
    m.edit_config(target='candidate', config=config)
except RPCError as e:
    print 'error:', e
else:
    print 'OK'

# get using xpath filter
print 'Get using XPath filter:',
expr = "aaa/authentication/users/user[name='testtailf']"
try:
    reply = m.get_config(source='candidate', filter=("xpath", expr))
except RPCError as e:
    print 'error:', e
else:
    print reply.data_xml

# get using subtree filter
print 'Get using subtree filter:',
criteria = """<aaa xmlns="http://tail-f.com/ns/aaa/1.1">
    <authentication>
	<users>
	    <user><name>testtailf</name></user>
	</users>
    </authentication>
</aaa>"""
try:
    reply = m.get_config(source='candidate', filter=("subtree", criteria))
except RPCError as e:
    print 'error:', e
else:
    print reply.data_xml

# modify user
print 'Modify user:',
config = """<config>
    <aaa xmlns="http://tail-f.com/ns/aaa/1.1">
	<authentication>
	    <users>
		<user>
            <name>testtailf</name>
		    <uid>9011</uid>
		    <homedir>abc123</homedir>
		</user>
	    </users>
	</authentication>
    </aaa>
</config>"""
try:
    reply = m.edit_config(target='candidate', config=config)
except RPCError as e:
    print 'error:', e
else:
    print 'OK'

print 'Deleting user:',
config = """<config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
    <aaa xmlns="http://tail-f.com/ns/aaa/1.1">
	<authentication>
	    <users>
		<user xc:operation="delete">
		    <name>testtailf</name>
		</user>
	    </users>
	</authentication>
    </aaa>
</config>"""
try:
    m.edit_config(target='candidate', config=config)
except RPCError as e:
    print 'error: ', e
else:
    print 'OK'

print 'Closing session:',
try:
    m.close_session()
except RPCError as e:
    print 'error', e
else:
    print 'OK'