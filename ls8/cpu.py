"""CPU functionality."""

import sys

HLT  =  0b00000001
MUL  =  0b10100010
LDI  =  0b10000010
PRN  =  0b01000111
PUSH =  0b01000101
POP  =  0b01000110
CALL =  0b01010000
RET  =  0b00010001
CMP  =  0b10100111
JMP  =  0b01010100
JEQ  =  0b01010101
JNE  =  0b01010110
ADD  =  0b10100000



class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 8
        self.ram = [0] * 256
        self.pc = 0
        self.registers = [0] * 8
        self.sp = 7
        self.fl = 6
        self.running = False

        self.operations = {}
        self.operations[HLT] = self.handle_HLT
        self.operations[LDI] = self.handle_LDI
        self.operations[MUL] = self.handle_MUL
        self.operations[PRN] = self.handle_PRN
        self.operations[PUSH] = self.handle_PUSH
        self.operations[POP] = self.handle_POP
        self.operations[CALL] = self.handle_CALL
        self.operations[RET] = self.handle_RET
        self.operations[CMP] = self.handle_CMP
        self.operations[JMP] = self.handle_JMP
        self.operations[JEQ] = self.handle_JEQ
        self.operations[JNE] = self.handle_JNE
        self.operations[ADD] = self.handle_ADD
        

         

    

    def load(self,file_name):
        """Load a program into memory."""

        address = 0
        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1

        if len(sys.argv) != 2:
            print("usage: ls8.py filename")
            sys.exit(1)

        progname = sys.argv[1]
        address = 0

        with open(progname) as f:
            for line in f:
                line = line.split("#")[0]
                line = line.strip()
                if line == "":
                    continue

                value = int(line, 2)
                # set the binary instruction to memory
                self.ram[address] = value
                address += 1  

    def ram_read(self, MAR):
        return self.ram[MAR]

    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == 'MUL':
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == 'DIV':
            self.reg[reg_a] /= self.reg[reg_b]
        elif op == "CMP":
            if self.reg[reg_a] == self.reg[reg_b]:
                self.fl = 0b00000001
            if self.reg[reg_a] < self.reg[reg_b]:
                self.fl = 0b00000010
            if self.reg[reg_a] > self.reg[reg_b]:
                self.fl = 0b00000011
        else:
            raise Exception("Unsupported ALU operation")

    def handle_HLT(self):
        self.running = False

    def handle_LDI(self):
        op_a = self.ram_read(self.pc+1)
        op_b = self.ram_read(self.pc+2)
        self.reg[op_a] = op_b
        self.pc += 3

    def handle_MUL(self):
        op_a = self.ram_read(self.pc+1)
        op_b = self.ram_read(self.pc+2)
        self.reg[op_a] = self.reg[op_a]*self.reg[op_b]
        self.pc += 3

    def handle_PRN(self):
        reg_num = self.ram_read(self.pc+1)
        print(self.reg[reg_num])
        self.pc += 2

    def handle_PUSH(self):
        ir = self.ram_read(self.pc)
        val = ir
        op_count = val >> 6  
        ir_len = 1 + op_count
        self.reg[7] -= 1
        reg_num = self.ram_read(self.pc+1)
        val = self.reg[reg_num]
        stack_pointer = self.reg[7]
        self.ram[stack_pointer] = val
        self.pc += ir_len

    def handle_POP(self):
        ir = self.ram_read(self.pc)
        val = ir
        op_count = val >> 6  
        ir_len = 1 + op_count
        stack_pointer = self.reg[7]
        reg_num = self.ram_read(self.pc+1)
        val = self.ram[stack_pointer]
        self.reg[reg_num] = val
        self.reg[7] += 1
        self.pc += ir_len

    def handle_CALL(self):
        given_reg = self.ram[self.pc + 1]
        self.sp -= 1
        self.ram[self.sp] = self.pc + 2
        self.pc = self.reg[given_reg]

    def handle_RET(self):
        self.pc = self.ram[self.sp]
        self.reg[7] += 1

    def handle_CMP(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        self.alu('CMP', operand_a, operand_b)
        self.pc += 3

    def handle_JMP(self):
        reg_index = self.ram_read(self.pc + 1)
        self.pc = self.reg[reg_index]

    def handle_JEQ(self):
        if self.fl == 0b00000001:
            reg_index = self.ram_read(self.pc + 1)
            self.pc = self.reg[reg_index]
        else:
            self.pc += 2

    def handle_JNE(self):
        if self.fl != 0b00000001:
            reg_index = self.ram_read(self.pc + 1)
            self.pc = self.reg[reg_index]
        else:
            self.pc += 2
    def handle_ADD(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        self.alu('ADD', operand_a, operand_b)
        self.pc += 3




    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        self.running = True
        while self.running:
            ir = self.ram_read(self.pc)
            if ir in self.operations:
                stuff = self.operations[ir]
                stuff()
