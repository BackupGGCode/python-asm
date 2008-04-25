import code_bytes
import registers



def _make_alu_proxy(name):
	def proxy(self, *args):
		return getattr(self.alu, name)(self, *args)
	return proxy

def _make_alu_proxy_reverse(name):
	def proxy(self, x):
		return getattr(self.alu, name)(x, self)
	return proxy

class Place:
	
	"""	A virtual place somewhere where a value can be stored.
	
	If we hold a value and we are a temporary register, the register 
	must be locked. If we need the temporary register, we must first 
	copy the value somewhere
	
	is_pinned -- True if we need to keep a value after use, otherwise
	the value can be discarded after its first use and the place can 
	be reused.
	
	is_temp -- True if the value is kept in some temporary register and
	should be moved somewhere else when the temporary register is needed.
	
	has_value -- True if the place contains a value.
	
	address -- contains some platform-dependent address of the place,
	probably together with its size etc.
	"""
	
	def __init__(self, address, is_temp, has_value):
		if address:
			self.address = address
			self.is_temp = False
			self.is_pinned = True
			self.has_value = True
		else:
			self.address = None
			self.is_temp = True
			self.is_pinned = False
			self.has_value = False
			
	def __del__(self):
		print 'del', self
			
	def make_not_temp(self):
		if self.is_temp:
			new_address = self.allocator.alloc(self)
			if self.has_value:
				self.allocator.copy_temp(self, new_address)
			self.address = new_address
			self.is_temp = False
			self.allocator.unlock_temp(self)
				
	def pin(self):
		self.is_pinned = True
			
	def free(self):
		''' Called when we do not need the value anymore'''
		if self.is_temp:
			if self.has_value:
				self.allocator.unlock_temp(self)
		else:
			self.allocator.free(self.address)
				
	def free_if_unpinned(self):
		if not self.is_pinned:
			self.free()
			
	def receive_value(self):
		self.has_value = True
		if self.is_temp:
			self.allocator.lock_temp(self)
			
	def get_value(self):
		return self
	
	set_value = _make_alu_proxy('set_value')
	
	__add__ = _make_alu_proxy('add_')
	__sub__ = _make_alu_proxy('sub_')
	__and__ = _make_alu_proxy('and_')
	__or__ = _make_alu_proxy('or_')
	__xor__ = _make_alu_proxy('xor_')
	
	__radd__ = _make_alu_proxy_reverse('add_')
	__rsub__ = _make_alu_proxy_reverse('sub_')
	__rand__ = _make_alu_proxy_reverse('and_')
	__ror__ = _make_alu_proxy_reverse('or_')
	__rxor__ = _make_alu_proxy_reverse('xor_')
	
	set_bit = _make_alu_proxy('set_bit')
	clear_bit = _make_alu_proxy('clear_bit')
	toggle_bit = _make_alu_proxy('toggle_bit')
			
class StaticAllocator:
	''' A simple allocator which allocates addresses from given list
	
	We have a single temporary register. 
	
	code_maker -- the thing that will generate instructions
	available -- the list of designators to choose from
	''' 
	 
	def __init__(self, code_maker, available):
		self._code_maker = code_maker
		self._available = available
		self._temp_value = None
		
	''' Allocates a free address to hold the given place'''
	def alloc(self, place):
		return self._available.pop()
	
	''' Frees the address previously allocated'''
	def free(self, address):
		assert address not in self._available
		self._available.append(address)
		
	''' Notifies that the value stored in the temporary register
	is not needed'''
	def unlock_temp(self, place):
		assert self._temp_value == place
		self._temp_value = None
		
	''' Notifies that a value was written to the temporary register
	and the given place holds it '''
	def lock_temp(self, place):
		assert self._temp_value is None
		self._temp_value = place
		place.address = registers.WREG.phys
	
	''' Copies the temporary register to the given address '''
	def copy_temp(self, place, address):
		assert self._temp_value == place
		self._code_maker.do('MOVWF', address)
		
	''' Copies the given place to the temporary register. The 
	temporary register must be free'''
	def copy_to_temp(self, place):
		assert self._temp_value is None
		if not place.is_temp:
			self._code_maker.do('MOVF', place.address, True)
			
	''' Frees the temporary register by moving its value elsewhere
	if needed'''
	def free_temp(self):
		if self._temp_value:
			self._temp_value.make_not_temp()
		

def _make_commutative_opt(op_lit, op_place):
	def f(self, place1, place2):
		if isinstance(place1, int):
			return self.binary_literal(place1, place2, op_lit, op_place)
		elif isinstance(place2, int):
			return self.binary_literal(place2, place1, op_lit, op_place)
		else:
			return self.binary_opt(place1, place2, op_place)
	return f
		
class ALU:
	''' Arithmetic logic unit	
	'''

	def __init__(self, code_maker, allocator):
		self._code_maker = code_maker
		self._allocator = allocator
		
	def binary(self, place1, place2, op):
		''' Do a binary operation without optimisations.
		
		Result is stored in place2 if it is not pinned and in temporary
		register otherwise
		
		op -- instruction name for arguments (temporary, place)
		'''
		assert place1.has_value
		assert place2.has_value
		# free place1
		place1.free_if_unpinned()
		# make sure the temporary register is free
		self._allocator.free_temp()
		# make sure the first argument is in the temporary register
		self._allocator.copy_to_temp(place1)
		
		if place2.is_pinned:
			res = Place(self, self._allocator)
			self._code_maker.do(op, place2.address, False)
			res.receive_value()
		else:
			self._code_maker.do(op, place2.address, True)
			res = place2
		return res
		
	def binary_literal(self, place1, place2, op_lit, op_place):
		''' Do a binary operation when place1 is literal
		
		op_lit -- instruction name for arguments (literal, temporary)
		op_place -- instruction name for arguments (temporary, place)
		'''
		assert place2.has_value
		assert isinstance(place1, int)
		assert place1>=-128 and place1<256
		place1 &= 0xff
		
		if place2.is_temp:
			place2.free_if_unpinned()
			self._allocator.free_temp()		
			self._code_maker.do(op_lit, place1)
			res = Place(self, self._allocator)
		else:
			self._allocator.free_temp()
			temp = Place(self, self._allocator)
			self._code_maker.do('MOVLW', place1)
			temp.receive_value()
			res = self.binary(temp, place2, op_place)
		return res
	
	def binary_opt(self, place1, place2, op1, op2=None):
		''' Tries to optimize a binary operation by swapping arguments'''
		if op2 is None:
			op2 = op1
		if place1.is_temp:
			return self.binary(place1, place2, op1)
		elif place2.is_temp:
			return self.binary(place2, place1, op2)
		elif not place1.is_pinned:
			return self.binary(place2, place1, op2)
		else:
			return self.binary(place1, place2, op1)
	
	add_ = _make_commutative_opt('ADDLW', 'ADDWF')
	and_ = _make_commutative_opt('ANDLW', 'ANDWF')
	or_ = _make_commutative_opt('IORLW', 'IORWF')
	xor_ = _make_commutative_opt('XORLW', 'XORWF')
		
	def sub_(self, place1, place2):
		if isinstance(place1, int):
			return self.binary_literal(place1, place2, 'SUBLW', 'SUBFWB')
		elif isinstance(place2, int):
			return self.binary_literal(-place2, place1, 'ADDLW', 'ADDWF')
		else:
			return self.binary_opt(place1, place2, 'SUBFWB', 'SUBWFB')
	
	def set_bit(self, place, n):
		self._code_maker.do('BSF', n, place.address)
		
	def clear_bit(self, place, n):
		self._code_maker.do('BCF', n, place.address)

	def toggle_bit(self, place, n):
		self._code_maker.do('BTG', n, place.address)
		
#	def set_value(self, place1, place2):
#		self._code_maker.do(
		
