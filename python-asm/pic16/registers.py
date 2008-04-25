import instructions
from utils import *

class PhysRegister(instructions.Designator):
    def __init__(self, name, address, length):
        self.name = name
        self.length = length
        instructions.Designator.__init__(self, address&0xff, False)

class LogRegister:
    def __init__(self, name, nbits, phys, offset):
        self.name = name
        self.nbits = nbits
        self.phys = phys
        self.offset = offset
    def designatorForBit(self, n=0):
        bitOffset = self.offset + n
        byteOffset = bitOffset//8
        assert byteOffset < self.phys.length
        return self.phys.designator(byteOffset)
    def translateBit(self, n=0):
        bitOffset = self.offset + n
        byteOffset = bitOffset//8
        assert byteOffset < self.phys.length
        return bitOffset - byteOffset*8

class FullRegister(LogRegister):
    def __init__(self, name, address, nbits):
        phys = PhysRegister(name, address, (nbits+7)//8)
        LogRegister.__init__(self, name, nbits, phys, 0)
        
class Field:
    name = ''
    pos1 = 0
    pos2 = 0
    def __init__(self, name, pos1, pos2):
        self.name = name
        self.pos1 = pos1
        self.pos2 = pos2
        
class FieldRegister(LogRegister):
    def __init__(self, field, recordReg):
        LogRegister.__init__(self, recordReg.name+'.'+field.name,
                        field.pos2 - field.pos1, recordReg.phys, field.pos1)

class RecordRegister(FullRegister):
    def __init__(self, name, address, length, fields):
        self.fields = {}
        FullRegister.__init__(self, name, address, 8*length)
        for f in fields:
            self.fields[f.name] = FieldRegister(f, self)
            
class BitSetRegister(RecordRegister):
    def __init__(self, name, address, length, availableMask):
        fields = []
        assert len(availableMask)==8*length
        mask = bits_to_bin(availableMask)
        for i in range(8*length):
            if (mask&(1<<i))!=0:
                fields.append(Field(str(i), i, i+1))
        RecordRegister.__init__(self, name, address, length, fields)
        for i in self.fields:
            self.fields[i] = self.fields[str(i)]

BSR = FullRegister('BSR', 0xfe0, 4)
WREG = FullRegister('WREG', 0xfe8, 8)

FSR = [
    FullRegister('FSR0', 0xfe9, 12), 
    FullRegister('FSR1', 0xfe1, 12),
    FullRegister('FSR2', 0xfd9, 12),
]

TOS = FullRegister('TOS', 0xffd, 20)
PCL = FullRegister('PCL', 0xff9, 20)
TBLPTR = FullRegister('TBLPTR', 0xff6, 20)

PROD = FullRegister('PROD', 0xff3, 16)
STATUS = BitSetRegister('STATUS', 0xfd8, 1, '00011111')
    