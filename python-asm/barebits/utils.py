# Copyright 2008 Anton Mellit

def bits_to_bin(str):
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
