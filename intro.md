# BareBits #

We develop a python library for machine code generation. Currently we have a first
minimal proof-of-concept version. It generates code for pic18fxxxx microcontrollers.

## Features ##

  * All instructions are callable via corresponding assembly names
  * We can write simple programs, without 'true' functions, but with 'macros', i.e. we may write python functions which generate some pieces of code to split a problem into smaller ones, but in the end we get one long function.
  * One can use statically allocated 8-bit variables
  * One can evaluate arithmetical expressions with operators +, -, &, ^, | in these variables like this:
```
x <<= y + z - t + 1
```
  * One can do comparisons <, >, ==, !=, <=, >= between results of operations and use them in control statements
  * One can use control statements if, for, while like this:
```
with while_(x < y):
    x += 1
```
  * Some commonly used registers are accessible by their names
  * Output is produced in well-known 'hex' format, which can be written to PIC using a programmer or a bootloader.

## Getting started ##

Simply download the source tree using the command below and play with test.py,
which contains some examples,

`svn checkout http://python-asm.googlecode.com/svn/trunk/ python-asm-read-only`

## License ##

This is distributed under LGPL (http://www.gnu.org/licenses/lgpl-3.0.txt)