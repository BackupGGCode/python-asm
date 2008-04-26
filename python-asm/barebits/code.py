# Copyright 2008 Anton Mellit

""" Basics of code generation """

from context import get_context, State

class CodeMaker(State):
    """ CodeMaker is used to generate instructions.
    
    output -- list of instructions generated. Each instruction is
    a Word instance,
    
    instructions -- dictionary of instructions available.
    
    """    
    def __init__(self, instructions, parent=None):
        self.instructions = instructions
        self.output = []
        self.parent = parent
    
    def do(self, name, *args):
        """ Append next instruction to the output """
        
        print name, args
        for word in self.instructions[name].write(*args):
            word.comments = [name]+list(args)
            self.output.append(word)
            
    def child(self):
        return CodeMaker(self.instructions, self)
        
def do(*args):
    """ Shortcut for get_context().code_maker.do(...) """
    get_context().code_maker.do(*args)
    
