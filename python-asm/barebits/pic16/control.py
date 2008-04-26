# Copyright 2008 Anton Mellit

""" Various control statements are implemented using 'with' statement """

from __future__ import with_statement

from contextlib import contextmanager, nested

from barebits.context import get_context, manage
from barebits.pic16.registers import STATUS
from barebits.pic16.alu import ALU, VariableManager
from barebits.pic16.instructions import standard, Designator
from barebits.allocator import StaticAllocator
from barebits.code import do, CodeMaker

"""
Recall that

conditions = ['zero': 0, 'not zero': 1, 'carry': 2, 'not carry': 3, 
        'overflow': 4, 'not overflow': 5, 'negative': 6, 'not negative': 7]
"""

_instr_branch = ['BZ', 'BNZ', 'BC', 'BNC', 'BOV', 'BNOV', 'BN', 'BNN']
_instr_skip = ['BTFSS', 'BTFSC', 'BTFSS', 'BTFSC', 
                    'BTFSS', 'BTFSC', 'BTFSS', 'BTFSC']
_status_bit = [2, 2, 0, 0, 3, 3, 4, 4]
_index_converse = [1, 0, 3, 2, 5, 4, 7, 6]

_status_reg = STATUS

def control_handler(f):
    def g(*args):
        with manage('allocator', 'var_manager', 'code_maker'):
            yield
            output = get_context().code_maker.output
        f(output, *args)
    return contextmanager(g)

def plug(output):
    get_context().code_maker.output.extend(output)

@control_handler
def block(output):
    plug(output)

@contextmanager
def program():
    """ Begins a program.
    
    Usage:
    
    with program():
        <program>
    
    """
    get_context().code_maker = CodeMaker(standard)
    get_context().allocator = StaticAllocator([Designator(x, True)
                                for x in range(0x40)])
    get_context().alu = ALU()
    get_context().var_manager = VariableManager()
    with block():
        yield

@control_handler
def if_(output, cond):
    """ if statement
    
    Usage:
    
    with if_(<condition>):
        <code>
    
    """
    to_check = get_context().alu.compute_bool(cond)
    length = len(output)
    if length<=0x7f:
        do(_instr_branch[_index_converse[to_check]], length)
    elif length<=0x3ff:
        do(_instr_skip[to_check], _status_reg, _status_bit[to_check])
        do('BRA', length)
    else:
        assert False
    plug(output)
    
@control_handler
def while_(output, cond):
    """ while statement
    
    Usage:
    
    with while_(<condition>):
        <code>
    
    """
    p0 = len(get_context().code_maker.output)
    to_check = get_context().alu.compute_bool(cond)
    length = len(output)
    if length<=0x7e:
        do(_instr_branch[_index_converse[to_check]], length+1)
    elif length<=0x3fe:
        do(_instr_skip[to_check], _status_reg, _status_bit[to_check])
        do('BRA', length+1)
    else:
        assert False
    plug(output)
    jump = p0 - len(get_context().code_maker.output) - 1
    assert jump >= -0x400
    do('BRA', jump)

@contextmanager
def for_(v, init, limit=None):
    """ for statement
    
    Usage:
    
    with for_(<variable>, <initial value>, <limit value>):
        <code>
    
    """
    if limit is None:
        limit = init
        init = 0
    v <<= init
    with while_(v < limit):
        yield
        v += 1

