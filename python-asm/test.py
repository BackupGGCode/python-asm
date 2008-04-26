

from __future__ import with_statement

from barebits.pic16.alu import Variable, var
from barebits.hex import gen_hex
from barebits.pic16.control import code, block, if_, while_, for_
from barebits.pic16.registers import TRIS28p, PORT28p
from barebits.context import get_context

def test1():
    with code():
        portTRIS = Variable(TRIS28p[1])
        port = Variable(PORT28p[1])

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
    with code():
        x = var()
        y = var()
        x <<= 2
        y <<= 3
        z = var(x-y)

    res = '\n'.join(gen_hex(get_context().code_maker.output, 0x100))
    print res
    assert res == '''
:020000040000fa
:0400000080ef00f09d
:0e010000020e3f6f030e3e6f3e513f5d3d6f9e
:00000001ff
'''.strip()
    
def pause():
    with block():
        x = var()
        with for_(x, 100):
            y = var()
            with for_(y, 100):
                z = var()
                with for_(z, 10):
                    pass
    
    
def test3():
    with code():
        portTRIS = Variable(TRIS28p[1])
        port = Variable(PORT28p[1])

        portTRIS.clear_bit(7)
        portTRIS.clear_bit(6)
        portTRIS.clear_bit(4)
        port.set_bit(7)
        port.clear_bit(6)
        port.clear_bit(4)
    
        with block():        
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
    assert res == '''
:020000040000fa
:0400000080ef00f09d
:10010000939e939c9398818e819c81983f513f5df3
:1001100040e13e51010f3e6f3e51010b000801e0ee
:10012000818e3e51010b000801e1819e3e51020b80
:10013000000801e0818c3e51020b000801e1819c26
:100140003e51040b000801e081883e51040b000879
:1001500001e18198000e3d6f3d516408e86c18e79d
:10016000000e3c6f3c516408e86c0ee7000e3b6fdc
:100170003b510a08e86c04e73b51010f3b6ff8d78d
:100180003c51010f3c6feed73d51010f3d6fe4d75d
:02019000bdd7d9
:00000001ff
'''.strip()

test1()
test2()
test3()
