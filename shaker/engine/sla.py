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
import collections
import operator as op
import re


class SLAException(Exception):
    pass


SLAItem = collections.namedtuple('SLAItem', ['record', 'state', 'expression'])
STATE_TRUE = 'OK'
STATE_FALSE = 'FAIL'

# supported operators
operators = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
             ast.Div: op.truediv, ast.Pow: op.pow, ast.BitXor: op.xor,
             ast.USub: op.neg, ast.Lt: op.lt, ast.Gt: op.gt, ast.LtE: op.le,
             ast.GtE: op.ge, ast.Eq: op.eq, ast.And: op.and_, ast.Or: op.or_,
             ast.Not: op.not_}


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
        r = ctx.get(node.id)
        if r is None:
            raise SLAException('Value "%s" is not found' % dump_ast_node(node))
        return r
    elif isinstance(node, ast.Str):
        return node.s
    elif isinstance(node, ast.BinOp):
        if isinstance(node.op, ast.RShift):
            return _eval_top(ctx, node)  # the top expression
        elif isinstance(node.op, ast.BitAnd):
            s = _eval(node.left, ctx)
            return ((s is not None) and
                    (re.match(_eval(node.right, ctx), s) is not None))
        else:
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
    elif isinstance(node, ast.BoolOp):
        r = _eval(node.values[0], ctx)
        for i in range(1, len(node.values)):
            r = operators[type(node.op)](r, _eval(node.values[i], ctx))
        return r
    elif isinstance(node, ast.Attribute):
        r = _eval(node.value, ctx).get(node.attr)
        if r is None:
            raise SLAException('Value "%s" is not found' % dump_ast_node(node))
        return r
    elif isinstance(node, ast.List):
        records = ctx
        filtered = []
        for record in records:
            for el in node.elts:
                if _eval(el, record):
                    filtered.append(record)
        return filtered
    else:
        raise TypeError(node)


def _eval_top(ctx, node):
    result = []
    # left -- array, right -- condition
    filtered = _eval(node.left, ctx)
    for record in filtered:
        try:
            right = _eval(node.right, record)
            state = (STATE_TRUE if right else STATE_FALSE)
        except (SLAException, TypeError) as e:
            state = str(e)
        result.append(SLAItem(record=record, state=state,
                              expression=dump_ast_node(node.right)))
    return result


def dump_ast_node(node):
    _operators = {ast.Add: '+', ast.Sub: '-', ast.Mult: '*',
                  ast.Div: '/', ast.Pow: '**', ast.BitXor: '^',
                  ast.BitAnd: '&', ast.BitOr: '|', ast.USub: '-',
                  ast.Lt: '<', ast.Gt: '>', ast.LtE: '<=', ast.GtE: '>=',
                  ast.Eq: '==', ast.And: 'and', ast.Or: 'or', ast.Not: 'not'}

    def _format(node):
        if isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Str):
            return '"%s"' % node.s
        elif isinstance(node, ast.BinOp):
            return '%s %s %s' % (_format(node.left), _operators[type(node.op)],
                                 _format(node.right))
        elif isinstance(node, ast.UnaryOp):
            return '%s %s' % (_operators[type(node.op)], _format(node.operand))
        elif isinstance(node, ast.Compare):
            r = '%s' % _format(node.left)
            for i in range(len(node.ops)):
                y = _format(node.comparators[i])
                r = '%s %s %s' % (r, _operators[type(node.ops[i])], y)
            return r
        elif isinstance(node, ast.BoolOp):
            return (' %s ' % _operators[type(node.op)]).join(
                _format(v) for v in node.values)
        elif isinstance(node, ast.Attribute):
            return '%s.%s' % (_format(node.value), node.attr)
        elif isinstance(node, ast.Expression):
            return '(%s)' % _format(node.body)
        else:
            raise TypeError(node)

    return _format(node)
