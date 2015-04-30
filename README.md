#Python-ASM
We want to use Python to develop low level code - operating systems, device drivers, etc. We should profit from describing hardware using some abstractions. We describe hardware in terms of _what_ can be done with it and _how_. We describe how something can be done in terms of how to _generate_ code which does it.

Since we may build some more complicated operations on top of less complicated, the code can be made very _portable_. Also we are very _flexible_ since we may use any feature of a particular hardware and we have _total control_ over the code we generate.

We start playing with microcontrollers the most accessible ones being microchip PIC. We plan to write a simple operating system for PICs with a shell. The OS should be able to communicate with different kinds of devices - PC via USB and RS-232, palm, ipod, some peripherals - servos, leds, buttons, etc.
