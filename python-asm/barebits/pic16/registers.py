# Copyright 2008 Anton Mellit

""" Registers of pic18f2455/2550/4455/4550 microcontrollers """

from barebits.pic16.instructions import Designator
from barebits.utils import bits_to_bin
from barebits.code import do

class SpecialRegister(Designator):
    """ A single-byte special function register """
    
    def __init__(self, name, address, nbits=8):
        assert address>=0xf60 and address<=0xfff
        self.name = name
        self.nbits = nbits
        Designator.__init__(self, address&0xff, False)


class LongRegister(SpecialRegister):
    """ Multi-byte register, several bytes which serve a common purpose

    Bits are numbered from first byte to last.

    nbytes -- number of bytes
    regs -- single-byte registers

    """
    def __init__(self, name, address, nbits):
        SpecialRegister.__init__(self, name, address, nbits)
        self.nbytes = (nbits - 1) // 8 + 1
        self.regs = []
        for i in range(self.nbytes):
            self.regs.append(SpecialRegister(name + str(i), address + i,
                            8 if i < self.nbytes-1 else nbits%8))


class Bit:
    """ Bit in a register

    reg -- single-byte register where the bit is
    ind -- index of bit

    """
    def __init__(self, reg, ind):
        self.reg = reg
        self.ind = ind


class BitRegister(LongRegister):
    """ BitRegister is just a sequence of bits

    bits -- list of bits, instances of Bit
    mask -- mask of available bits (string of '0' and '1', on __init__
    converted to a number)

    """
    def __init__(self, name, address, mask):
        LongRegister.__init__(self, name, address, len(mask))
        self.mask = bits_to_bin(mask)
        self.bits = [None] * len(mask)
        for i in range(len(mask)):
            if (self.mask&(1<<i)) != 0:
                self.bits[i] = Bit(self.regs[i//8], i%8)

    def __getitem__(self, ind):
        return self.bits[ind]


class Field(Bit):
    """ Field is a sequence of bits in a single-byte register

    pos1, pos2 -- bits are taken in range(pos1, pos2)
    nbits -- pos2 - pos1
    
    """
    def __init__(self, reg, name, pos1, pos2):
        Bit.__init__(self, reg, pos1)
        self.name = name
        self.pos1 = pos1
        self.pos2 = pos2
        self.nbits = pos2 - pos1


class FieldRegister(LongRegister):
    """ FieldRegister is a sequence of fields

    fields -- initialized with a list of pairs (name, length), one pair for
    each field, where name can be None, which means that the corresponding
    bits are not available, length is the number of bits in a field. After
    initialization fields contain a list of instances of Field

    """
    def __init__(self, name, address, fields):
        self.fields = {}
        nbits = 0
        for f in fields:
            nbits += f[1]
        LongRegister.__init__(self, name, address, nbits)
        pos = 0
        for f in fields:
            if f[0]:
                setattr(self, f[0], Field(self.regs[pos//8], f[0],
                                    pos, pos + f[1]))
            pos += f[1]
        

def field_bits(*names):
    """ Converts 'A', 'B', ... to ('A', 1), ('B', 1), ... """
    for name in names:
        yield (name, 1)


class FSRControl:
    """ Registers related to indirect data memory function.

    FSR -- memory pointer
    PLUSW -- add WREG to FSR and use the value (the value of FSR does
    not change)
    PREINC -- increment FSR and use the value
    POSTINC -- use the value and increment FSR
    POSTDEC -- use the value and decrement FSR
    INDF -- use the value

    """
    def __init__(self, ind, address):
        self.FSR = LongRegister('FSR'+str(ind), address, 12)
        self.PLUSW = SpecialRegister('PLUSW'+str(ind), address+2)
        self.PREINC = SpecialRegister('PREINC'+str(ind), address+3)
        self.POSTDEC = SpecialRegister('POSTDEC'+str(ind), address+4)
        self.POSTINC = SpecialRegister('POSTINC'+str(ind), address+5)
        self.INDF = SpecialRegister('INDF'+str(ind), address+6)
        

BSR = SpecialRegister('BSR', 0xfe0, 4) # Bank select register
WREG = SpecialRegister('WREG', 0xfe8) # Working register
STATUS = FieldRegister('STATUS', 0xfd8, field_bits('C', 'DC', 'Z', 'OV', 'N'))

FSR_controls = [ # indirect data memory
    FSRControl(0, 0xfe9),
    FSRControl(1, 0xfe1),
    FSRControl(2, 0xfd9),
]

TOS = LongRegister('TOS', 0xffd, 20) # Top of stack
STKPTR = FieldRegister('STKPTR', 0xffc, [('SP', 5), (None, 1), ('UNF', 1),
                                        ('FUL', 1)])

PCL = LongRegister('PCL', 0xff9, 20) # Holding register

TBLPTR = LongRegister('TBLPTR', 0xff6, 21) # Program memory table pointer
TABLAT = SpecialRegister('TABLAT', 0xff5) # Program memory table latch

PROD = LongRegister('PROD', 0xff3, 16) # Product register

""" Interrupt controller """
INTCON = FieldRegister('INTCON', 0xff0, field_bits(
    'INT1IF', 'INT2IF', None, 'INT1IE', 'INT2IE', None, 'INT1IP', 'INT2IP',
    'RBIP', None, 'TMR0IP', None, 'INTEDG2', 'INTEDG1', 'INTEDG0', 'nRBPU',
    'RBIF', 'INT0IF', 'TMR0IF', 'RBIE', 'INT0IE', 'TMR0IE', 'PEIE', 'GIE'))

""" Timers """
TMR = [
    LongRegister('TMR0', 0xfd6, 16),
    LongRegister('TMR1', 0xfce, 16),
    SpecialRegister('TMR2', 0xfcc),
    LongRegister('TMR3', 0xfb2, 16),
]

""" Port directions """
TRIS28p = [
    BitRegister('TRISA', 0xf92, '01111111'),
    BitRegister('TRISB', 0xf93, '11111111'),
    BitRegister('TRISC', 0xf94, '11000111'),
]

TRIS40p = TRIS28p + [
    BitRegister('TRISD', 0xf95, '11111111'),
    BitRegister('TRISE', 0xf96, '00000111'),
]

LAT28p = [
    BitRegister('LATA', 0xf89, '01111111'),
    BitRegister('LATB', 0xf8a, '11111111'),
    BitRegister('LATC', 0xf8b, '11000111'),
]

LAT40p = LAT28p + [
    BitRegister('LATD', 0xf8c, '11111111'),
    BitRegister('LATE', 0xf8d, '00000111'),
]

""" Ports """
PORT28p = [
    BitRegister('PORTA', 0xf80, '01111111'),
    BitRegister('PORTB', 0xf81, '11111111'),
    BitRegister('PORTC', 0xf82, '11000111'),
]

PORT40p = PORT28p + [
    BitRegister('PORTD', 0xf83, '11111111'),
    BitRegister('PORTE', 0xf84, '00000111'),
]

""" Timer 0 control """
T0CON = FieldRegister('T0CON', 0xfd5, [('T0PS', 3), ('PSA', 1),
                    ('T0SE', 1), ('T0CS', 1), ('T08bit', 1), ('TMR0ON', 1)])

""" Oscillator control """
OSCCON = FieldRegister('OSCCON', 0xfd3, [('SCS', 2), ('IOFS', 1),
                    ('OSTS', 1), ('IRCF', 3), ('IDLEN', 1)])

