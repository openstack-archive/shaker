# Copyright (c) 2015 Mirantis Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import ast
import operator as op

import logging as std_logging
import os
import random

from oslo_config import cfg
from oslo_log import log as logging
import six


LOG = logging.getLogger(__name__)


def env(*_vars, **kwargs):
    """Returns the first environment variable set.

    If none are non-empty, defaults to '' or keyword arg default.
    """
    for v in _vars:
        value = os.environ.get(v)
        if value:
            return value
    return kwargs.get('default', None)


def validate_required_opts(conf, opts):
    # all config parameters default to ENV values, that's why standard
    # check of required options doesn't work and needs to be done manually
    for opt in opts:
        if opt.required and not conf[opt.dest]:
            raise cfg.RequiredOptError(opt.name)


def init_config_and_logging(opts):
    conf = cfg.CONF
    conf.register_cli_opts(opts)
    conf.register_opts(opts)
    logging.register_options(conf)
    logging.set_defaults()

    try:
        conf(project='shaker')
        validate_required_opts(conf, opts)
    except cfg.RequiredOptError as e:
        print('Error: %s' % e)
        conf.print_usage()
        exit(1)

    logging.setup(conf, 'shaker')
    LOG.info('Logging enabled')
    conf.log_opt_values(LOG, std_logging.DEBUG)


def read_file(file_name, base_dir=''):
    full_path = os.path.normpath(os.path.join(base_dir, file_name))
    if not os.path.exists(full_path):
        # treat file_name as relative to shaker's package root
        full_path = os.path.normpath(os.path.join(
            os.path.dirname(__import__('shaker').__file__), '../', file_name))
        if not os.path.exists(full_path):
            msg = ('File %s not found by absolute nor by relative path' %
                   file_name)
            LOG.error(msg)
            raise IOError(msg)

    fd = None
    try:
        fd = open(full_path)
        return fd.read()
    except IOError as e:
        LOG.error('Error reading file: %s', e)
        raise
    finally:
        if fd:
            fd.close()


def write_file(data, file_name, base_dir=''):
    full_path = os.path.normpath(os.path.join(base_dir, file_name))
    fd = None
    try:
        fd = open(full_path, 'w')
        return fd.write(data)
    except IOError as e:
        LOG.error('Error writing file: %s', e)
        raise
    finally:
        if fd:
            fd.close()


def split_address(address):
    try:
        host, port = address.split(':')
    except ValueError:
        raise ValueError('Invalid address: %s, "host:port" expected', address)
    return host, port


def read_uri(uri):
    try:
        req = six.moves.urllib.request.Request(url=uri)
        fd = six.moves.urllib.request.urlopen(req)
        raw = fd.read()
        fd.close()
        return raw
    except Exception as e:
        LOG.warn('Error "%(error)s" while reading uri %(uri)s',
                 {'error': e, 'uri': uri})


def random_string(length=6):
    return ''.join(random.sample('adefikmoprstuz', length))


def copy_dict_kv(source):
    return dict((k, v) for k, v in source.items())


def flatten_dict(d, prefix='', sep='.'):
    res = []
    for k, v in d.items():
        path = prefix + k
        if isinstance(v, dict):
            res.extend(flatten_dict(v, path + sep))
        else:
            res.append((path, v))
    return res


# supported operators
operators = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
             ast.Div: op.truediv, ast.Pow: op.pow, ast.BitXor: op.xor,
             ast.USub: op.neg, ast.Lt: op.lt, ast.Gt: op.gt, ast.LtE: op.le,
             ast.GtE: op.ge, ast.Eq: op.eq}


def eval_expr(expr, ctx=None):
    """Usage examples:

    >>> eval_expr('2^6')
    4
    >>> eval_expr('2**6')
    64
    >>> eval_expr('1 + 2*3**(4^5) / (6 + -7)')
    -5.0
    >>> eval_expr('11 > a > 5', {'a': 7})
    True
    >>> eval_expr('2 + a.b', {'a': {'b': 2.2}})
    4.2
    """
    ctx = ctx or {}
    return _eval(ast.parse(expr, mode='eval').body, ctx)


def _eval(node, ctx):
    if isinstance(node, ast.Num):
        return node.n
    elif isinstance(node, ast.Name):
        return ctx.get(node.id)
    elif isinstance(node, ast.BinOp):
        return operators[type(node.op)](_eval(node.left, ctx),
                                        _eval(node.right, ctx))
    elif isinstance(node, ast.UnaryOp):
        return operators[type(node.op)](_eval(node.operand, ctx))
    elif isinstance(node, ast.Compare):
        x = _eval(node.left, ctx)
        r = True
        for i in range(len(node.ops)):
            y = _eval(node.comparators[i], ctx)
            r &= operators[type(node.ops[i])](x, y)
            x = y
        return r
    elif isinstance(node, ast.Attribute):
        return _eval(node.value, ctx).get(node.attr)
    else:
        raise TypeError(node)
