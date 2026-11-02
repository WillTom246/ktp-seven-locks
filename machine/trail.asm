; The little machine uses 8-bit unsigned registers.
; Numerical literals use Python notation: 0x (hex), 0b (binary), or decimal.
MOV R0, 0x1A
MOV R1, 0b0011
SHL R1, 1
XOR R0, R1
SUB R0, 0x15
PRINT R0
