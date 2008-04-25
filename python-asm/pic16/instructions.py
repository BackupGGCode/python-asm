from utils import bits_to_bin

class Instruction:
    '''An instruction may have parameters'''
    
    def __init__(self, name, length, opcode, nbits):
        opcode = opcode.replace(' ', '')
        self.name = name
        self.length = length
        self.opcode = bits_to_bin(opcode)
        self.nbits = nbits
        assert (len(opcode)==nbits)
    
    def write(self, *params):
        assert False # abstract
        
        
class Designator:
    
    def __init__(self, address, use_bsr):
        self.address = address
        self.use_bsr = use_bsr
        assert address>=0 and address<=255
        
    def encode(self):
        return (self.use_bsr<<8) | self.address
    
    def __repr__(self):
        res = hex(self.address)
        if self.use_bsr:
            res += ' (BSR)'
        else:
            res += ' (ACCESS)'
        return  res
    

class Word:
    def __init__(self, word):
        self.word = word


class SimpleInstr(Instruction):
    
    def __init__(self, name, opcode):
        Instruction.__init__(self, name, 2, opcode, 16)
        
    def write(self, codeBytes):
        yield Word(self.opcode)
        

def genInstrCode(opcode, address, nbits):
    res = opcode<<nbits
    res |= address&((1<<nbits)-1)
    return Word(res)


class ArgInstr(Instruction):
    
    def __init__(self, name, opcode, argbits):
        Instruction.__init__(self, name, 2, opcode, 16-argbits)
        
    def write(self, arg):
        yield genInstrCode(self.opcode, arg, 16-self.nbits)
        

def designatorInstrCode(opcode, designator):
    res = opcode<<9
    res |= designator.encode()
    return Word(res)


class DesignatorInstr(Instruction):
    
    def __init__(self, name, opcode):
        Instruction.__init__(self, name, 2, opcode, 16-9)
        
    def write(self, designator):
        yield designatorInstrCode(self.opcode, designator)


def designatorDestInstrCode(opcode, designator, toSource):
    res = opcode<<10
    res |= toSource<<9
    res |= designator.encode()
    return Word(res)


class DesignatorDestInstr(Instruction):
    
    def __init__(self, name, opcode):
        Instruction.__init__(self, name, 2, opcode, 16-9-1)
        
    def write(self, designator, toSource):
        yield designatorDestInstrCode(self.opcode, designator, toSource)
    

class MoveInstr(Instruction):
    
    def __init__(self, name, opcode):
        Instruction.__init__(self, name, 4, opcode, 16-12)
    
    def write(self, srcAddress, dstAddress):
        yield genInstrCode(self.opcode, srcAddress) # 1100 ffff ffff ffff
        yield genInstrCode(NOPcode, dstAddress) # 1111 ffff ffff ffff
        

def bitInstrCode(opcode, designator, nbit):
    res = opcode<<12
    res |= nbit<<9
    res |= designator.encode()
    return Word(res)
        

class BitInstr(Instruction):
    
    def __init__(self, name, opcode):
        Instruction.__init__(self, name, 2, opcode, 16-9-3)
        
    def write(self, nbit, designator):
        yield bitInstrCode(self.opcode, designator, nbit)
    

class LongJumpInstr(Instruction):
    
    def __init__(self, name, opcode):
        Instruction.__init__(self, name, 4, opcode, 16-8)
    
    def write(self, address):
        yield genInstrCode(self.opcode, address&0xff, 8)
        yield genInstrCode(NOPcode, (address>>8)&0xfff, 12)
        
        
def fsrInstrCode(opcode, fsr, val, argbits):
    res = opcode<<(argbits+2)
    res |= fsr<<argbits
    res |= val
    return Word(res)


class FSRInstr(Instruction):
    
    def __init__(self, name, opcode):
        Instruction.__init__(self, name, 2, opcode, 16-6-2)
    
    def write(self, fsr, value):
        yield fsrInstrCode(self.opcode, fsr, value, 6)

class LongFSRInstr(Instruction):
    
    def __init__(self, name, opcode):
        Instruction.__init__(self, name, 4, opcode, 16-4-2)
    
    def write(self, fsr, value):
        yield fsrInstrCode(self.opcode, fsr, (value>>8)&0xf, 4)
        yield genInstrCode(NOPcode, value&0xff, 8)
        

class MoveIndInstr(Instruction):
    def __init__(self, name, opcode):
        Instruction.__init__(self, name, 4, opcode, 16-7)
    def write(self, offset, address):
        yield genInstrCode(self.opcode, offset, 7)
        yield genInstrCode(NOPcode, address)
        

NOPcode = 0xf

standardInstructionSet = [
    SimpleInstr('NOP', 				'0000 0000 0000 0000'),
    SimpleInstr('SLEEP', 			'0000 0000 0000 0011'),
    SimpleInstr('CLRWDT', 			'0000 0000 0000 0100'),
    SimpleInstr('PUSH', 			'0000 0000 0000 0101'),
    SimpleInstr('POP', 				'0000 0000 0000 0110'),
    SimpleInstr('DAW', 				'0000 0000 0000 0111'),
    SimpleInstr('TBLRD', 			'0000 0000 0000 1000'),
    SimpleInstr('TBLRDPOSTINC', 	'0000 0000 0000 1001'),
    SimpleInstr('TBLRDPOSTDEC', 	'0000 0000 0000 1010'),
    SimpleInstr('TBLRDPREINC', 		'0000 0000 0000 1011'),
    SimpleInstr('TBLWT', 			'0000 0000 0000 1100'),
    SimpleInstr('TBLWTPOSTINC',		'0000 0000 0000 1101'),
    SimpleInstr('TBLWTPOSTDEC',		'0000 0000 0000 1110'),
    SimpleInstr('TBLWTPREINC', 		'0000 0000 0000 1111'),
    SimpleInstr('RETFIE', 			'0000 0000 0001 0000'),
    SimpleInstr('RETFIEFAST',		'0000 0000 0001 0001'),
    SimpleInstr('RETURN', 			'0000 0000 0001 0010'),
    SimpleInstr('RETURNFAST',		'0000 0000 0001 0011'),
    SimpleInstr('RESET', 			'0000 0000 1111 1111'),
    ArgInstr('MOVLB', 				'0000 0001 0000', 4),
    DesignatorInstr('MULWF', 		'0000 001'),
    DesignatorDestInstr('DECF',		'0000 01'),
    ArgInstr('SUBLW', 				'0000 1000', 8),
    ArgInstr('IORLW', 				'0000 1001', 8),
    ArgInstr('XORLW', 				'0000 1010', 8),
    ArgInstr('ANDLW', 				'0000 1011', 8),
    ArgInstr('RETLW', 				'0000 1100', 8),
    ArgInstr('MULLW', 				'0000 1101', 8),
    ArgInstr('MOVLW', 				'0000 1110', 8),
    ArgInstr('ADDLW', 				'0000 1111', 8),
    DesignatorDestInstr('IORWF', 	'0001 00'),
    DesignatorDestInstr('ANDWF', 	'0001 01'),
    DesignatorDestInstr('XORWF', 	'0001 10'),
    DesignatorDestInstr('COMF', 	'0001 11'),
    DesignatorDestInstr('ADDWFC', 	'0010 00'),
    DesignatorDestInstr('ADDWF', 	'0010 01'),
    DesignatorDestInstr('INCF', 	'0010 10'),
    DesignatorDestInstr('DECFSZ', 	'0010 11'),
    DesignatorDestInstr('RRCF', 	'0011 00'),
    DesignatorDestInstr('RLCF', 	'0011 01'),
    DesignatorDestInstr('SWAPF', 	'0011 10'),
    DesignatorDestInstr('INCFSZ', 	'0011 11'),
    DesignatorDestInstr('RRNCF', 	'0100 00'),
    DesignatorDestInstr('RLNCF', 	'0100 01'),
    DesignatorDestInstr('INFSNZ', 	'0100 10'),
    DesignatorDestInstr('DCFSNZ', 	'0100 11'),
    DesignatorDestInstr('MOVF', 	'0101 00'),
    DesignatorDestInstr('SUBFWB', 	'0101 01'),
    DesignatorDestInstr('SUBWFB', 	'0101 10'),
    DesignatorDestInstr('SUBWF', 	'0101 11'),
    DesignatorInstr('CPFSLT', 		'0110 000'),
    DesignatorInstr('CPFSEQ', 		'0110 001'),
    DesignatorInstr('CPFSGT', 		'0110 010'),
    DesignatorInstr('TSTFSZ', 		'0110 011'),
    DesignatorInstr('SETF', 		'0110 100'),
    DesignatorInstr('CLRF', 		'0110 101'),
    DesignatorInstr('NEGF', 		'0110 110'),
    DesignatorInstr('MOVWF', 		'0110 111'),
    BitInstr('BTG', 				'0111'),
    BitInstr('BSF', 				'1000'),
    BitInstr('BCF', 				'1001'),
    BitInstr('BTFSS', 				'1010'),
    BitInstr('BTFSC', 				'1011'),
    MoveInstr('MOVFF', 				'1100'),
    ArgInstr('BRA',					'1101 0', 11),
    ArgInstr('RCALL', 				'1101 1', 11),
    ArgInstr('BZ', 					'1110 0000', 8),
    ArgInstr('BNZ', 				'1110 0001', 8),
    ArgInstr('BC', 					'1110 0010', 8),
    ArgInstr('BNC', 				'1110 0011', 8),
    ArgInstr('BOV', 				'1110 0100', 8),
    ArgInstr('BNOV', 				'1110 0101', 8),
    ArgInstr('BN', 					'1110 0110', 8),
    ArgInstr('BNN', 				'1110 0111', 8),
    LongJumpInstr('CALL', 			'1110 1100'),
    LongJumpInstr('CALLFAST', 		'1110 1101'),
    LongJumpInstr('GOTO', 			'1110 1111'),
    LongFSRInstr('LFSR', 				'1110 1110 00'),
    ArgInstr('NOP1',				'1111', 12),
]

extendedInstructionSet = [
    SimpleInstr('CALLW', 			'0000 0000 0001 0100'),
    FSRInstr('ADDFSR', 				'1110 1000'),
    FSRInstr('SUBFSR', 				'1110 1001'),
    ArgInstr('ADDULNK',				'1110 1000 11', 6),
    ArgInstr('SUBULNK',				'1110 1001 11', 6),
    ArgInstr('PUSHL',				'1110 1010', 8),
    MoveIndInstr('MOVSF',			'1110 1011 0'),
    MoveIndInstr('MOVSS',			'1110 1011 1'),
]
