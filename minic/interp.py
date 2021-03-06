# interp.py
"""
Intérprete
==========

Este es un intérprete que puede ejecutar programas minic directamente
desde el código IR generado.  Esto se puede usar para verificar los
resultados sin requerir una dependencia de JVM.

Para ejecutar un programa utiliza:

    bash % python3 -m interp someprogram.c

"""
import sys


class Interpreter(object):
    """
    Ejecuta un intérprete en el código intermedio SSA generado
    para su compilador. La idea de implementación es la siguiente.
    Dada una secuencia de tuplas de instrucción tales como:

        code = [
            ('MOVI', 1, 'R1'),
            ('MOVI', 2, 'R2'),
            ('ADDI', 'R1', 'R2', 'R3'),
            ('PRINTI', 'R3')
        ...
        ]

    La clase ejecuta los métodos self.run_opcode(args).  Por ejemplo:

        self.run_MOVI(1, 'R1')
        self.run_MOVI(2, 'R2')
        self.run_ADDI('R1','R2','R3')
        self.run_PRINTI('R3')
    """

    def __init__(self):
        # Registers
        self.registers = {}

        # Global variables storage
        self.global_vars = {}

        # Local variables storage
        self.local_vars = {}

    def execute(self, code):
        for function in code:
            self.local_vars = {}
            for inst, *args in function:
                getattr(self, f'run_{inst}')(*args)
            print("locals: ", self.local_vars)
        print("gobals: ", self.global_vars)

    # Interpreter opcodes

    def run_MOVI(self, value, target):
        self.registers[target] = value

    run_MOVF = run_MOVI
    run_MOVB = run_MOVI

    def run_ADDI(self, left, right, target):
        self.registers[target] = self.registers[left] + self.registers[right]

    run_ADDF = run_ADDI

    def run_SUBI(self, left, right, target):
        self.registers[target] = self.registers[left] - self.registers[right]

    run_SUBF = run_SUBI

    def run_MULI(self, left, right, target):
        self.registers[target] = self.registers[left] * self.registers[right]

    run_MULF = run_MULI

    def run_DIVI(self, left, right, target):
        self.registers[target] = self.registers[left] // self.registers[right]

    def run_DIVF(self, left, right, target):
        self.registers[target] = self.registers[left] / self.registers[right]

    def run_REMI(self, left, right, target):
        self.registers[target] = self.registers[left] % self.registers[right]

    def run_XOR(self, left, right, target):
        self.registers[target] = self.registers[left] ^ self.registers[right]

    def run_PRINTI(self, value):
        print(self.registers[value])

    run_PRINTF = run_PRINTI

    def run_PRINTB(self, value):
        print(chr(self.registers[value]), end='')
        sys.stdout.flush()

    def run_VARI(self, name):
        self.global_vars[name] = 0

    def run_VARF(self, name):
        self.global_vars[name] = 0.0

    run_VARB = run_VARI

    def run_ALLOCI(self, name):
        self.local_vars[name] = 0

    def run_ALLOCF(self, name):
        self.local_vars[name] = 0.0

    run_ALLOCB = run_VARI

    def run_LOADI(self, name, target):
        if name in self.local_vars:
            self.registers[target] = self.local_vars[name]
        else:
            self.registers[target] = self.global_vars[name]

    run_LOADF = run_LOADI
    run_LOADB = run_LOADI

    def run_STOREI(self, target, name):
        if name in self.local_vars:
            self.local_vars[name] = self.registers[target]
        else:
            self.global_vars[name] = self.registers[target]

    run_STOREF = run_STOREI
    run_STOREB = run_STOREI


# ----------------------------------------------------------------------
#                       NO MODIFIQUE NADA DESDE AQUÍ
# ----------------------------------------------------------------------

def main():
    import sys
    from ircode import compile_ircode
    from errors import errors_reported

    if len(sys.argv) != 2:
        sys.stderr.write('Usage: python3 -m minic.interp filename\n')
        raise SystemExit(1)

    source = open(sys.argv[1]).read()
    code = compile_ircode(source)
    if not errors_reported():
        interpreter = Interpreter()
        interpreter.execute(code)


if __name__ == '__main__':
    main()

