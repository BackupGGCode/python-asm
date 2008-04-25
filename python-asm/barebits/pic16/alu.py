# Copyright 2008 Anton Mellit

import registers
import operations

from context import get_context, State
from allocator import alloc, free
from code import do


def _make_alu_proxy(name):
    def proxy(self, *args):
        return getattr(get_context().alu, name)(self, *args)
    return proxy


class Variable(operations.Variable):
    
    def __init__(self, address):
        self.address = address
        
    assign = _make_alu_proxy('assign')
    set_bit = _make_alu_proxy('set_bit')
    clear_bit = _make_alu_proxy('clear_bit')
    toggle_bit = _make_alu_proxy('toggle_bit')
        

class VariableManager(State):
            
    def __init__(self, vars = None):
        if vars is None:
            self.parent_vars = []
        else:
            self.parent_vars = vars			
        self.vars = []
        
    def create_var(self):
        address = alloc()
        var = Variable(address)
        self.vars.append(var)
        return var
        
    def child(self):
        return VariableManager(self.parent_vars + self.vars)
    
    def close(self):
        print 'close var_manager'
        for var in self.vars:
            free(var.address)
            var.address = None


def var(value = None):
    v = get_context().var_manager.create_var()
    if(value):
        v <<= value
    return v

_wreg = registers.WREG.phys

_instr_wreg_reg = {'+': 'ADDWF', '&': 'ANDWF', '|': 'IORWF', '^': 'XORWF'}
_instr_reg_wreg = dict(_instr_wreg_reg)
_instr_wreg_reg['-'] = 'SUBFWB'
_instr_reg_wreg['-'] = 'SUBWF'
_instr_lit_wreg = {'+': 'ADDLW', '&': 'ANDLW', '|': 'IORLW', '^': 'XORLW', '-': 'SUBLW'}

conditions = {'zero': 0, 'not zero': 1, 'carry': 2, 'not carry': 3, 'overflow': 4, 
                'not overflow': 5, 'negative': 6, 'not negative': 7}

_comp_flip = {'<': '>', '<=': '>=', '==': '==', '<>': '<>', '>': '<', '>=': '<='}

class StatusAddress:
    pass

class ALU:
    def assign(self, target, expression):
        self._compute(target.address, expression)
        
    def _compute(self, addr, expr):
        if hasattr(expr, 'opname'):
            self._compute_op(addr, expr)
        elif hasattr(expr, 'address'):
            self._copy(addr, expr.address)
        else:
            self._copy_int(addr, int(expr))

    def _compute_op(self, addr, expr):
        if expr.opname in operations.binary_ops:
            self._binary(addr, expr)
        elif expr.opname in operations.unary_ops:
            self._unary(addr, name, *args)
        else:
            assert False
            
    def _binary(self, addr, expr):
        to_free = []
        (arg1, arg2) = expr.args
        
        res_addr = None
        
        if hasattr(arg2, 'opname'):
            if hasattr(arg1, 'opname'):
                self._compute_op(None, arg1)
                res_addr = arg1.address
                to_free.append(res_addr)
            self._compute_op(_wreg, arg2)
        else:
            if hasattr(arg1, 'opname'):
                self._compute_op(_wreg, arg1)
        
        if addr:
            res_addr = addr
            
        if res_addr is None:
            res_addr = alloc()
        
        expr.address = res_addr
        
        if hasattr(arg1, 'address') and hasattr(arg2, 'address'):
            self._binary_reg(res_addr, expr.opname, arg1.address, arg2.address)
        else:
            self._binary_literal(res_addr, expr.opname, arg1, arg2)
        
        for a in to_free:
            if a != res_addr:
                free(a)
        
    def _binary_reg(self, target, name, src1, src2):
        src = None
        
        if src1 == _wreg:
            src = src2
        elif src2 == _wreg:
            src = src1
        else:
            src = src1
            self._copy(_wreg, src2)
            src2 = _wreg
        
        if name in operations.binary_ops:
            to_source = (src == target)
        
            if src1 == _wreg:
                if name=='-':
                    do('BSF', 0, registers.STATUS.phys)				
                do(_instr_wreg_reg[name], src, to_source)
            else:
                do(_instr_reg_wreg[name], src, to_source)
            
            if not to_source:
                src = _wreg
                    
            if target!=src:
                self._copy(target, src)
        else:
            if src1 == _wreg:
                self._compare_wreg_reg(target, name, src)
            else:
                self._compare_wreg_reg(target, _comp_flip[name], src)	
            
    def _binary_literal(self, target, name, src1, src2):
        res_addr = None
        if not hasattr(src1, 'address'):
            if src2.address != _wreg:
                self._copy(_wreg, src2.address)
            if name in operations.binary_ops:
                do(_instr_lit_wreg[name], int(src1))
                if target!=_wreg:
                    self._copy(target, _wreg)
            else:
                self._compare_lit_wreg(target, name, int(src1))
        else:
            if name in operations.commutative_ops:
                self._binary_literal(target, name, src2, src1)
            elif name in operations.comp_ops:
                self._binary_literal(target, _comp_flip[name], src2, src1)
            elif name=='-':
                self._binary_literal(target, '+', -int(src2), src1)
            else:
                assert false

    def _copy(self, target, src):
        if target==src:
            return
        elif target==_wreg:
            do('MOVF', src, False)
        elif src==_wreg:
            do('MOVWF', target)
        else:
            do('MOVFF', src, target)
            
    
    def _copy_int(self, target, src):
        if target==_wreg:
            do('MOVLW', src)
        else:
            self._copy_int(_wreg, src)
            self._copy(target, _wreg)

    def set_bit(self, var, n):
        do('BSF', n, var.address)
        
    def clear_bit(self, var, n):
        do('BCF', n, var.address)

    def toggle_bit(self, var, n):
        do('BTG', n, var.address)
        
    def compute_bool(self, expr):
        if expr.opname in operations.comp_ops:
            self._binary(StatusAddress(), expr)
        else:
            assert False
        return conditions[expr.address.cond]
        
    def _compare(self, target, name):
        if name == '==':
            target.cond = 'zero'
        elif name == '<>':
            target.cond = 'not zero'
        elif name == '<':
            target.cond = 'negative'
        elif name == '>=':
            target.cond = 'not negative'
        else:
            do('NEGF', _wreg)
            if name == '>':
                target.cond = 'negative'
            elif name == '<=':
                target.cond = 'not negative'
            else:
                assert False		
    
    def _compare_wreg_reg(self, target, name, reg):
        do('SUBWF', reg, False) # reg - wreg
        self._compare(target, _comp_flip[name])
    
    def _compare_lit_wreg(self, target, name, lit):
        do('SUBLW', lit) # lit - wreg
        self._compare(target, name)
    