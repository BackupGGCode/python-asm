import instructions

class CPU:
    names = ['pic18f2455', 'pic18f2550', 'pic18f4455', 'pic18f4550']
    standard = {}
    extended = {}
    current = standard
    for x in instructions.standardInstructionSet:
        standard[x.name] = x
    for x in instructions.extendedInstructionSet:
        extended[x.name] = x
    extended.update(standard)

cpu = CPU()
