# Copyright 2008 Anton Mellit

""" Utility functions """

def bits_to_bin(str):
    """ Converts a string of '0' and '1' to a number """
    res = 0
    for c in str:
        res <<= 1
        if c=='0':
            pass
        elif c=='1':
            res += 1
        else:
            assert False 
    return res

def list_to_dict(L):
    """ Converts a list of objects with name attribute to a dictionary """
    res = {}
    for x in L:
        res[x.name] = x
    return res
