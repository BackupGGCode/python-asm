# Copyright 2008 Anton Mellit

from __future__ import with_statement

from contextlib import contextmanager
from context import get_context
from registers import STATUS
import alu

'''
Recall that

conditions = ['zero': 0, 'not zero': 1, 'carry': 2, 'not carry': 3, 'overflow': 4, 
                'not overflow': 5, 'negative': 6, 'not negative': 7]
'''

_instr_branch = ['BZ', 'BNZ', 'BC', 'BNC', 'BOV', 'BNOV', 'BN', 'BNN']
_instr_skip = ['BTFSS', 'BTFSC', 'BTFSS', 'BTFSC', 'BTFSS', 'BTFSC', 'BTFSS', 'BTFSC']
_status_bit = [2, 2, 0, 0, 3, 3, 4, 4]
_index_converse = [1, 0, 3, 2, 5, 4, 7, 6]

_status_reg = STATUS.phys

@contextmanager
def if_(cond):
    to_check = get_context().alu.compute_bool(cond)
    parent_code = get_context().code_maker
    with get_context().manager():
        yield
        length = len(get_context().code_maker.output)
        if length<=0x7f:
            parent_code.do(_instr_branch[_index_converse[to_check]], length)
        elif length<=0x3ff:
            parent_code.do(_instr_skip[to_check], _status_bit[to_check], _status_reg)
            parent_code.do('BRA', length)
        else:
            assert False
    
@contextmanager
def while_(cond):
    parent_code = get_context().code_maker
    p0 = len(parent_code.output)
    to_check = get_context().alu.compute_bool(cond)
    with get_context().manager():
        yield
        length = len(get_context().code_maker.output)
        if length<=0x7e:
            parent_code.do(_instr_branch[_index_converse[to_check]], length+1)
        elif length<=0x3fe:
            parent_code.do(_instr_skip[to_check], _status_bit[to_check], _status_reg)
            parent_code.do('BRA', length+1)
        else:
            assert False
    jump = p0 - len(parent_code.output) - 1
    assert jump >= -0x400
    parent_code.do('BRA', jump)

@contextmanager
def for_(v, init, limit=None):
    if limit is None:
        limit = init
        init = 0
    v <<= init
    with while_(v < limit):
        yield
        v += 1


    