# Copyright 2008 Anton Mellit

import contextlib

class Context: pass


class State:
    
    def child(self):
        return self
    
    def close(self):
        pass
        

class StateManager(object):
    def __init__(self, attr_name):
        self.attr_name = attr_name
    
    def __enter__(self): 
        oldvalue = getattr(get_context(), self.attr_name)
        newvalue = oldvalue.child()
        newvalue.__oldvalue = oldvalue
        setattr(get_context(), self.attr_name, newvalue)
        
    def __exit__(self, type, *args):
        if type is None:
            newvalue = getattr(get_context(), self.attr_name)
            oldvalue = newvalue.__oldvalue
            newvalue.close()
            newvalue.__oldvalue = None
            setattr(get_context(), self.attr_name, oldvalue)
        

_context = Context()

_context.manager = contextlib.nested

def get_context():
    return _context

def manage(*attr_names):
    res = [StateManager(name) for name in attr_names]
    return contextlib.nested(*res)
