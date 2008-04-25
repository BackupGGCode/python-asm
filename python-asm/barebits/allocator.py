# Copyright 2008 Anton Mellit

import context

class StaticAllocator(context.State):
    ''' A simple allocator which allocates addresses from a given list

    available -- the list of addresses to choose from
    '''

    def __init__(self, available):
        self._available = available
        self._used = []

    ''' Allocates a free address'''
    def alloc(self):
        address = self._available.pop()
        self._used.append(address)
        return address

    ''' Frees the address previously allocated'''
    def free(self, address):
        assert address in self._used
        self._used.remove(address)
        self._available.append(address)

    def child(self):
        return StaticAllocator(list(self._available))

    def close(self):
        print 'close allocator'
        assert not self._used

def alloc():
    return context.get_context().allocator.alloc()

def free(address):
    context.get_context().allocator.free(address)
