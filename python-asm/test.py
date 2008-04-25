from __future__ import with_statement

import cpu
from allocator import StaticAllocator
from code import CodeMaker
from io import *
from alu import ALU, VariableManager, Variable, var
from instructions import Designator
from context import get_context, install_manager, StateManager
from hex import gen_hex
from control import if_, while_, for_

for key in ['allocator', 'var_manager', 'code_maker']:
    install_manager(StateManager(key))

def test1():
    get_context().code_maker = CodeMaker(cpu.cpu.standard)
    get_context().allocator = StaticAllocator([Designator(x, True) for x in range(0x40)])
    get_context().alu = ALU()
    get_context().var_manager = VariableManager()
        
    with get_context().manager():
        portTRIS = Variable(TRIS28p[1].phys)
        port = Variable(PORT28p[1].phys)

        portTRIS.clear_bit(7)
        port.set_bit(7)

        port <<= (port+3)+(portTRIS+6)-(5-port)

    res = '\n'.join(gen_hex(get_context().code_maker.output, 0x100))
    print res
    assert res == '''
:020000040000fa
:0400000080ef00f09d
:10010000939e818e8150030f3f6f9350060f3f27c0
:08011000815005083f5d816e7e
:00000001ff
'''.strip()

def test2():
    get_context().code_maker = CodeMaker(cpu.cpu.standard)
    get_context().allocator = StaticAllocator([Designator(x, True) for x in range(0x40)])
    get_context().alu = ALU()
    get_context().var_manager = VariableManager()
        
    with get_context().manager():
        x = var()
        y = var()
        x <<= 2
        y <<= 3
        z = var(x-y)

    res = '\n'.join(gen_hex(get_context().code_maker.output, 0x100))
    print res
    
def pause():
    with get_context().manager():
        x = var()
        with for_(x, 100):
            y = var()
            with for_(y, 100):
                z = var()
                with for_(z, 10):
                    pass
    
    
def test3():
    get_context().code_maker = CodeMaker(cpu.cpu.standard)
    get_context().allocator = StaticAllocator([Designator(x, True) for x in range(0x40)])
    get_context().alu = ALU()
    get_context().var_manager = VariableManager()
    
    portTRIS = Variable(TRIS28p[1].phys)
    port = Variable(PORT28p[1].phys)

    portTRIS.clear_bit(7)
    portTRIS.clear_bit(6)
    portTRIS.clear_bit(4)
    port.set_bit(7)
    port.clear_bit(6)
    port.clear_bit(4)
    
    with get_context().manager():        
        x = var()
        y = var()
        with while_(x == x):
            y <<= y + 1
            with if_(y&1 != 0) :
                port.set_bit(7)
            with if_(y&1 == 0) :
                port.clear_bit(7)
            with if_(y&2 != 0) :
                port.set_bit(6)
            with if_(y&2 == 0) :
                port.clear_bit(6)
            with if_(y&4 != 0) :
                port.set_bit(4)
            with if_(y&4 == 0) :
                port.clear_bit(4)                
            pause()
    res = '\n'.join(gen_hex(get_context().code_maker.output, 0x100))
    print res

test1()
test2()
test3()
