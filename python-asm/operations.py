
def _op_stub(name):
    def f(*args):
        return Operation(name, args)
    return f
    
def _op_rstub(name):
    def f(arg1, arg2):
        return Operation(name, (arg2, arg1))
    return f

def _op_istub(name):
    def f(self, arg):
        self.assign(Operation(name, (self, arg)))
        return self
    return f
        
def _op_stubs(name):
    return (_op_stub(name), _op_rstub(name), _op_istub(name))

binary_ops = ['+', '^', '|', '&', '-']
unary_ops = ['u-', 'id']
commutative_ops = ['+', '^', '|', '&']
comp_ops = ['<', '<=', '==', '<>', '>', '>=']

class Variable:
    
    (__add__, __radd__, __iadd__) = _op_stubs('+')
    (__xor__, __rxor__, __ixor__) = _op_stubs('^')
    (__or__, __ror__, __ior__) = _op_stubs('|')
    (__and__, __rand__, __iand__) = _op_stubs('&')
    (__sub__, __rsub__, __isub__) = _op_stubs('-')
    (__lt__, __le__, __eq__, __ne__, __gt__, __ge__) = (_op_stub(x) for x in
                    ('<', '<=', '==', '<>', '>', '>='))
    
    def get_value(self):
        return self
    
    def set_value(self, val):
        self.assign(val)
        return self
    
    value = property(get_value, set_value)
        
    __ilshift__ = set_value
    

class Operation(Variable):
    
    def __init__(self, name, args):
        self.opname = name
        self.args = args
