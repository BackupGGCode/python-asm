from registers import *

TMR = [
    FullRegister('TMR0', 0xfd6, 16),
    FullRegister('TMR1', 0xfce, 16),
    FullRegister('TMR2', 0xfcc, 8),
    FullRegister('TMR3', 0xfb2, 16),
]

TRIS28p = [
    BitSetRegister('TRISA', 0xf92, 1, '01111111'),
    BitSetRegister('TRISB', 0xf93, 1, '11111111'),
    BitSetRegister('TRISC', 0xf94, 1, '11000111'),
]

TRIS40p = TRIS28p + [
    BitSetRegister('TRISD', 0xf95, 1, '11111111'),
    BitSetRegister('TRISE', 0xf96, 1, '00000111'),
]

LAT28p = [
    BitSetRegister('LATA', 0xf89, 1, '01111111'),
    BitSetRegister('LATB', 0xf8a, 1, '11111111'),
    BitSetRegister('LATC', 0xf8b, 1, '11000111'),
]

LAT40p = LAT28p + [
    BitSetRegister('LATD', 0xf8c, 1, '11111111'),
    BitSetRegister('LATE', 0xf8d, 1, '00000111'),
]

PORT28p = [
    BitSetRegister('PORTA', 0xf80, 1, '01111111'),
    BitSetRegister('PORTB', 0xf81, 1, '11111111'),
    BitSetRegister('PORTC', 0xf82, 1, '11000111'),
]

PORT40p = PORT28p + [
    BitSetRegister('PORTD', 0xf83, 1, '11111111'),
    BitSetRegister('PORTE', 0xf84, 1, '00000111'),
]

