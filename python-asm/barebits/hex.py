import cpu

hex = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']

def wordsToBytes(words):
    for w in words:
        if hasattr(w, 'comments'):
            print w.comments
        yield w.word & 0xff
        yield (w.word>>8) & 0xff

def to_hex(val, len):
    s = ''
    for i in range(len):
        s = hex[val&0xf] + s
        val = val>>4
    return s

def hex_line(address, type, data):
    s = ':'
    sum = 0
    s += to_hex(len(data), 2)
    sum -= len(data)
    s += to_hex(address, 4)
    sum -= address&0xff
    sum -= (address>>8)&0xff
    s += to_hex(type, 2)
    sum -= type
    sum &= 0xff
    for c in data:
        s += to_hex(c, 2)
        sum -= c
        sum &= 0xff
    s += to_hex(sum, 2)
    return s

def gen_hex(output, offset):
    yield hex_line(0, 4, [0, 0])
    
    goto = wordsToBytes(cpu.cpu.standard['GOTO'].write(offset>>1))
    yield hex_line(0, 0, list(goto))
    
    bytes = list(wordsToBytes(output))
    
    count = (len(bytes)+15)//16
    for i in range(count):
        buf = [bytes[x] for x in range(i*16, min((i+1)*16, len(bytes)))]
        yield hex_line(offset+i*16, 0, buf)
    yield hex_line(0, 1, [])

