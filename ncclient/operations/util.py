#!/usr/bin/env python

'Boilerplate'

from ncclient import OperationError

from . import MissingCapabilityError

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
        raise MissingCapabilityError('[%s] capability is required for this operation' % key)


def store_or_url(store, url):
    one_of(store, url)
    node = {}
    if store is not None:
        node['tag'] = store
    else:
        node['tag'] = 'url'
        node['text'] = url
    return node

def build_filter(spec, type, criteria):
    filter = {
        'tag': 'filter',
        'attributes': {'type': type}
    }
    if type == 'subtree':
        filter['children'] = [criteria]
    elif type == 'xpath':
        filter['attributes']['select'] = criteria
    return filter
