#!/usr/bin/env python

'boilerplate'

from ncclient import OperationError

class MissingCapabilityError(OperationError):
    pass

def one_of(self, *args):
    for i, arg in enumerate(args):
        if arg is not None:
            for argh in args[i+1:]:
                if argh is not None:
                    raise OperationError('Too many parameters')
            else:
                return
    raise OperationError('Insufficient parameters')


def assert_capability(key, capabilities):
    if key not in capabilities:
        raise MissingCapabilityError


def store_or_url(store, url):
    one_of(store, url)
    node = {}
    if store is not None:
        node['tag'] = store
    else:
        node['tag'] = 'url'
        node['text'] = url
    return node
