#!/usr/bin/env python3
"""Tiny 8-bit educational VM: MOV, ADD, SUB, XOR, SHL, SHR, PRINT."""
import sys
from pathlib import Path


def run(program):
    regs = {f'R{i}': 0 for i in range(4)}

    def value(tok):
        tok = tok.upper()
        if tok in regs:
            return regs[tok]
        return int(tok, 0)

    for line_number, line in enumerate(program.splitlines(), 1):
        line = line.split(';', 1)[0].strip()
        if not line:
            continue
        op, *args = line.replace(',', ' ').split()
        op = op.upper()
        args = [arg.upper() for arg in args]
        if op == 'PRINT' and len(args) == 1:
            print(value(args[0]))
        elif op in ('MOV', 'ADD', 'SUB', 'XOR', 'SHL', 'SHR') and len(args) == 2:
            target, rhs = args
            if target not in regs:
                raise ValueError(f'Line {line_number}: invalid register {target}')
            a, b = regs[target], value(rhs)
            regs[target] = {
                'MOV': lambda: b,
                'ADD': lambda: a + b,
                'SUB': lambda: a - b,
                'XOR': lambda: a ^ b,
                'SHL': lambda: a << b,
                'SHR': lambda: a >> b,
            }[op]() & 0xFF
        else:
            raise ValueError(f'Line {line_number}: bad instruction {line!r}')

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit('Usage: python3 tools/mini_cpu.py machine/trail.asm')
    run(Path(sys.argv[1]).read_text(encoding='utf-8'))
