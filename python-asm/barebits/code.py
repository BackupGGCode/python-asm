from context import get_context, State

class CodeMaker(State):
    
    def __init__(self, instructions, parent=None):
        self.instructions = instructions
        self.output = []
        self.parent = parent
    
    def do(self, name, *args):
        print name, args
        for word in self.instructions[name].write(*args):
            word.comments = [name]+list(args)
            self.output.append(word)
            
    def child(self):
        return CodeMaker(self.instructions, self)
    
    def close(self):
        if self.parent:
            self.parent.output.extend(self.output)
    
        
def do(*args):
    get_context().code_maker.do(*args)
    
