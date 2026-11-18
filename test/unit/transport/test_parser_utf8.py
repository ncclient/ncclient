"""Inbound UTF-8 framing through the default parser and RPC listeners."""

import pytest

from ncclient import manager
from ncclient.operations.retrieve import Get
from ncclient.transport.session import NetconfBase
from ncclient.transport.ssh import SSHSession


NS = 'urn:ietf:params:xml:ns:netconf:base:1.0'
DELIM = b']]>]]>'


def rpc_session(base):
    handler = manager.make_device_handler({'name': 'default'})
    session = SSHSession(handler)
    session._base = base
    session._connected = True
    return session, handler


def request(session, handler, value):
    rpc = Get(session, handler, async_mode=True).request()
    reply = ('<rpc-reply xmlns="%s" message-id="%s">'
             '<data><value>%s</value></data></rpc-reply>'
             % (NS, rpc.id, value)).encode('utf-8')
    return rpc, reply


def chunked(parts):
    chunks = [b'\n#%d\n' % len(part) + part for part in parts]
    return b''.join(chunks) + b'\n##\n'


def assert_reply(rpc, value):
    assert rpc.event.is_set()
    assert rpc.error is None
    assert rpc.reply.ok
    assert rpc.reply.data_ele.find('{%s}value' % NS).text == value


@pytest.mark.parametrize('value', ['Zürich', '東京', 'router😀'])
@pytest.mark.parametrize('base', [NetconfBase.BASE_10, NetconfBase.BASE_11])
def test_every_read_boundary_reaches_rpc_listener(base, value):
    # Every byte split includes splits inside 2-, 3- and 4-byte characters,
    # inside headers/terminators, and between completed and partial replies.
    session, handler = rpc_session(base)
    _, reply = request(session, handler, value)
    wire = reply + DELIM if base == NetconfBase.BASE_10 else chunked([reply])
    for split in range(1, len(wire)):
        session, handler = rpc_session(base)
        rpc, reply = request(session, handler, value)
        wire = (reply + DELIM if base == NetconfBase.BASE_10
                else chunked([reply]))
        if split >= len(wire):
            break
        session.parser.parse(wire[:split])
        assert not rpc.event.is_set()
        session.parser.parse(wire[split:])
        assert_reply(rpc, value)


@pytest.mark.parametrize('value', ['Zürich', '東京', 'router😀'])
def test_every_chunk_boundary_reaches_rpc_listener(value):
    for split in range(1, 170):
        session, handler = rpc_session(NetconfBase.BASE_11)
        rpc, reply = request(session, handler, value)
        if split >= len(reply):
            break
        session.parser.parse(chunked([reply[:split], reply[split:]]))
        assert_reply(rpc, value)


@pytest.mark.parametrize('base', [NetconfBase.BASE_10, NetconfBase.BASE_11])
def test_complete_reply_then_partial_unicode_reply(base):
    session, handler = rpc_session(base)
    first, reply1 = request(session, handler, 'first')
    second, reply2 = request(session, handler, 'Zürich')
    split = reply2.index('ü'.encode()) + 1
    if base == NetconfBase.BASE_10:
        initial = reply1 + DELIM + reply2[:split]
        remainder = reply2[split:] + DELIM
    else:
        initial = chunked([reply1]) + b'\n#%d\n' % split + reply2[:split]
        remainder = chunked([reply2[split:]])
    session.parser.parse(initial)
    assert_reply(first, 'first')
    assert not second.event.is_set()
    session.parser.parse(remainder)
    assert_reply(second, 'Zürich')
    assert session._buffer.getvalue() == b''
    assert session._message_list == []


@pytest.mark.parametrize('base', [NetconfBase.BASE_10, NetconfBase.BASE_11])
def test_invalid_utf8_still_rejected_when_message_complete(base):
    session, handler = rpc_session(base)
    rpc, reply = request(session, handler, 'invalid')
    reply = reply.replace(b'invalid', b'\xff')
    wire = reply + DELIM if base == NetconfBase.BASE_10 else chunked([reply])
    with pytest.raises(UnicodeDecodeError):
        session.parser.parse(wire)
    assert not rpc.event.is_set()
