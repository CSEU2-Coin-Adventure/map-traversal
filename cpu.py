import sys

LDI = 0b10000010
PRN = 0b01000111 
MUL = 0b10100010
ADD = 0b10100000
HLT = 0b00000001 
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RTN = 0b00010001
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110
AND = 0b10101000
OR = 0b10101010
XOR = 0b10101011
NOT = 0b01101001
SHL = 0b10101100
SHR = 0b10101101
MOD = 0b10100010
PRA = 0b01001000

class CPU:
    def __init__(self):
        self.pc = 0
        self.ir = 0
        self.running = True
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.fl = 0b00000000

        self.reg[7] = 0xf4
        self.SP = self.reg[7]

    def load(self):
        f = open("machine-code.txt", "r")
        address = 0
        for line in f:
            ln = ''
            for char in line:
                if char == '#':
                    break
                if char == '\n':
                    break
                ln += char
            if len(ln) > 0:
                self.ram[address] = int(ln, 2)
                address += 1

    def branch_table(self, op_1, op_2):
        if self.ir & 0b1 << 5:
            self.alu(self.ir, op_1, op_2)

        else:
            branches = {
                LDI: self.handle_ldi,
                PRN: self.handle_prn,
                HLT: self.handle_hlt,
                PUSH: self.push,
                POP: self.pop,
                CALL: self.call,
                RTN: self.rtn,
                JMP: self.handle_jmp,
                JEQ: self.handle_jeq,
                JNE: self.handle_jne,
                PRA: self.handle_pra
            }

            branches[self.ir](op_1, op_2)

    def ram_read(self, mar):
        if mar <= len(self.ram) - 1:
            return self.ram[mar]
        return 0

    def ram_write(self, mar, mdr):
        self.ram[mar] = mdr

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        if op == ADD:
            self.reg[reg_a] += self.reg[reg_b]
        # elif op == "SUB": etc
        elif op == MUL:
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == CMP:
            # compare reg_a and reg_b
            # if equal set E flag to 1 otherwise 0
            if self.reg[reg_a] == self.reg[reg_b]:
                self.fl = 0b00000001
            # if a < b set L flag to 1 otherwise 0
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.fl = 0b00000100
            # if a > b set G flag to 1 otherwise 0
            else:
                self.fl = 0b00000010
        elif op == AND:
            self.reg[reg_a] = self.reg[reg_a] & self.reg[reg_b]
        elif op == OR:
            self.reg[reg_a] = self.reg[reg_a] | self.reg[reg_b]
        elif op == NOT:
            self.reg[reg_a] = not self.reg[reg_a]
        elif op == XOR:
            self.reg[reg_a] = self.reg[reg_a] ^ self.reg[reg_b]
        elif op == SHL:
            self.reg[reg_a] = self.reg[reg_a] << self.reg[reg_b]
        elif op == SHR:
            self.reg[reg_a] = self.reg[reg_a] >> self.reg[reg_b]
        elif op == MOD:
            self.reg[reg_a] = self.reg[reg_a] % self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def handle_ldi(self, op_a, op_b):
        self.reg[op_a] = op_b

    def handle_prn(self, op_a, _op_b):
        print(self.reg[op_a])

    def handle_hlt(self, _op_a, _op_b):
        self.running = False

    def handle_jmp(self, op_a, _op_b):
        # jmp to the address in the given register
        self.pc = self.reg[op_a]

    def handle_jeq(self, op_a, _op_b):
        # if flag E is 1 jmp to the address in the given register
        if self.fl % 2 != 0:
            self.ir = JMP
            self.handle_jmp(op_a, None)

    def handle_jne(self, op_a, _op_b):
        # if flag E is 1 jmp to the address in the given register
        if self.fl % 2 == 0:
            self.ir = JMP
            self.handle_jmp(op_a, None) 

    def handle_pra(self, op_a, _op_b):
        n = self.reg[op_a]
        print(chr(n))

    def push(self, op_a, _op_b):
        # decrement stack pointer
        self.reg[self.SP] -= 1
        self.ram[self.reg[self.SP]] = self.reg[op_a]

    def push_value(self, op_a):
        self.reg[self.SP] -= 1
        self.ram[self.reg[self.SP]] = op_a

    def pop(self, op_a, _op_b):
        self.reg[op_a] = self.ram[self.reg[self.SP]]
        self.reg[self.SP] += 1

    def pop_value(self):
        value = self.ram[self.reg[self.SP]]
        self.reg[self.SP] += 1 
        return value

    def call(self, op_a, op_b):
        # push the address of the next instruction onto the stack
        ir = self.ram_read(self.pc)
        next_address = self.pc + 1 + (ir >> 6)
        self.push_value(next_address)
        # move pc to subroutine address
        self.pc = self.reg[op_a]

    def rtn(self, op_a, op_b):
        self.pc = self.pop_value()

    def should_advance(self, ir):
        if ir == CALL:
            return False
        elif ir == RTN:
            return False
        elif ir == JMP:
            return False
        else:
            return True

    def run(self):
        """Run the CPU."""
        while self.running:
        # set memory at pc counter to intruction register
            self.ir = self.ram_read(self.pc)
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            # self.branch_table[self.ir](operand_a, operand_b)
            self.branch_table(operand_a, operand_b)
            
            if self.should_advance(self.ir):
                self.pc += 1 + (self.ir >> 6)