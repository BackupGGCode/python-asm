import code_bytes
import registers
import instructions
from cpu import cpu


class ALU(code_bytes.CodeMaker):
	def __init__(self):
		code_bytes.CodeMaker.__init__(self)
		gpreg = registers.WREG
			
	def bitInstr(self, name, reg, n):
		cpu.standard[name].write(self.codeBytes, reg.translateBit(n), 
			reg.designatorForBit(n))
	
	def byteInstr(self, name, reg, dir=False):
		assert isinstance(reg, registers.FullRegister)
		assert reg.phys.length==1
		if isinstance(cpu.standard[name], instructions.DesignatorDestInstr):
			cpu.standard[name].write(self.codeBytes, reg.designatorForBit(), dir)
		else:
			cpu.standard[name].write(self.codeBytes, reg.designatorForBit())
	
	def setBit(self, reg, n=0):
		self.bitInstr('BSF', reg, n)
		
	def clearBit(self, reg, n=0):
		self.bitInstr('BCF', reg, n)

	def toggleBit(self, reg, n=0):
		self.bitInstr('BTF', reg, n)
	
	def addToGP(self, reg):
		if isinstance(reg, int):
			self.literalInstr('ADDLW', reg)
		else:
			self.byteInstr('ADDWF', reg, False)
		 
	def addGP(self, reg):
		self.byteInstr('ADDWF', reg, True)
		
	def subFromGPBorrow(self, reg):
		self.byteInstr('SUBFWB', reg, False)
	
	def subFromGPBorrowToReg(self, reg):
		self.byteInstr('SUBFWB', reg, True)
			
	def subGP(self, reg):
		self.byteInstr('SUBWF', reg, True)
		
	def subGPToGP(self, reg):
		self.byteInstr('SUBWF', reg, False)
		
	def subGPBorrow(self, reg):
		self.byteInstr('SUBWFB', reg, True)
		
	def subGPBorrowToGP(self, reg):
		self.byteInstr('SUBWFB', reg, False)
		
	def skipIfGP(self, reg):
		self.byteInstr('CPFSEQ', reg, False)
		
	def skipIfGTGP(self, reg):
		self.byteInstr('CPFSGT', reg, False)
	
	def skipIfLTGP(self, reg):
		self.byteInstr('CPFSLT', reg, False)
	