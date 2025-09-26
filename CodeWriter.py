from Parser import CommandType


class CodeWriter:
    def __init__(self, output_file_path):
        """
        Opens the output file for writing and prepares for code generation.
        """
        self.output_file = open(output_file_path, 'w')
        self.label_counter = 0  # To generate unique labels
        self.segment_registers = {  # Map segments to their base registers
            'local': 'LCL',
            'argument': 'ARG',
            'this': 'THIS',
            'that': 'THAT'
        }

    def _write_pop(self, segment, index):
        """Helper to write code for popping to a memory segment."""
        assembly_code = []
        if segment == 'temp':
            target_addr = 5 + index
            assembly_code.extend([
                f'// pop temp {index}',
                f'@{target_addr}',
                'D=A',              # D = 5 + index (target address)
                '@R13',
                'M=D',              # R13 = target address (temp storage)
                '@SP',
                'M=M-1',            # SP--
                'A=M',              # A = SP (top of stack)
                'D=M',              # D = *SP (value to pop)
                '@R13',
                'A=M',              # A = target address
                'M=D'               # *address = value
            ])
        else:  
            base_reg = self.segment_registers.get(segment)
            if base_reg is None:
                raise ValueError(f'Unsupported segment for pop: {segment}')
            assembly_code.extend([
                f'// pop {segment} {index}',
                f'@{index}',
                'D=A',              # D = index
                f'@{base_reg}',
                'D=D+M',            # D = LCL + index (target address)
                '@R13',
                'M=D',              # R13 = target address (temp storage)
                '@SP',
                'M=M-1',            # SP--
                'A=M',              # A = SP (top of stack)
                'D=M',              # D = *SP (value to pop)
                '@R13',
                'A=M',              # A = target address
                'M=D'               # *address = value
            ])
        return assembly_code

    def _write_binary_op(self, operation):
        """Helper to write code for binary operations."""
        return [
            '@SP',
            'M=M-1',
            'A=M',
            'D=M',
            '@SP',
            'M=M-1',
            'A=M',
            operation,  # The only line that changes
            '@SP',
            'M=M+1'
        ]

    def write_arithmetic(self, command):
        """Writes the assembly code for the given arithmetic command."""
        assembly_code = []
        if command == 'add':
            assembly_code.extend(self._write_binary_op('M=D+M'))
        elif command == 'sub':
            assembly_code.extend(self._write_binary_op('M=M-D'))
        elif command == 'and':
            assembly_code.extend(self._write_binary_op('M=D&M'))
        elif command == 'or':
            assembly_code.extend(self._write_binary_op('M=D|M'))
        elif command == 'eq':
            # Generate unique labels for this comparison
            true_label = f'EQ_TRUE_{self.label_counter}'
            end_label = f'EQ_END_{self.label_counter}'
            self.label_counter += 1

            assembly_code.extend([
                f'// eq',
                '@SP',
                'M=M-1',    # Decrement SP
                'A=M',
                'D=M',      # D = y (first value)
                '@SP',
                'M=M-1',    # Decrement SP
                'A=M',
                'D=M-D',    # D = x - y
                f'@{true_label}',
                'D;JEQ',    # If x == y (D is zero), jump to TRUE case

                # False case: set D to 0
                'D=0',
                f'@{end_label}',
                '0;JMP',    # Unconditionally jump to the end

                # True case: set D to -1
                f'({true_label})',
                'D=-1',

                # Push the result from D onto the stack
                f'({end_label})',
                '@SP',
                'A=M',
                'M=D',      # *SP = D (which is 0 or -1)
                '@SP',
                'M=M+1'     # SP++
            ])
        elif command == 'lt':
            # Generate unique labels for this comparison
            true_label = f'LT_TRUE_{self.label_counter}'
            end_label = f'LT_END_{self.label_counter}'
            self.label_counter += 1

            assembly_code.extend([
                f'// lt',
                '@SP',
                'M=M-1',
                'A=M',
                'D=M',      # D = y
                '@SP',
                'M=M-1',
                'A=M',
                'D=M-D',    # D = x - y
                f'@{true_label}',
                'D;JLT',    # If x < y (D is negative), jump to TRUE

                # False case: set D to 0
                'D=0',
                f'@{end_label}',
                '0;JMP',

                # True case: set D to -1
                f'({true_label})',
                'D=-1',

                # Push the result from D onto the stack
                f'({end_label})',
                '@SP',
                'A=M',
                'M=D',
                '@SP',
                'M=M+1'
            ])
        elif command == 'gt':
            # Generate unique labels for this comparison
            true_label = f'GT_TRUE_{self.label_counter}'
            end_label = f'GT_END_{self.label_counter}'
            self.label_counter += 1

            assembly_code.extend([
                f'// gt',
                '@SP',
                'M=M-1',
                'A=M',
                'D=M',      # D = y
                '@SP',
                'M=M-1',
                'A=M',
                'D=M-D',    # D = x - y
                f'@{true_label}',
                'D;JGT',    # If x > y (D is positive), jump to TRUE

                # False case: set D to 0
                'D=0',
                f'@{end_label}',
                '0;JMP',

                # True case: set D to -1
                f'({true_label})',
                'D=-1',

                # Push the result from D onto the stack
                f'({end_label})',
                '@SP',
                'A=M',
                'M=D',
                '@SP',
                'M=M+1'
            ])
        elif command == 'neg':
            assembly_code.extend([
                '// neg',
                '@SP',
                'M=M-1',    # Point to the top of the stack
                'A=M',      # Get the address
                'M=-M',     # Negate the value in place
                '@SP',
                'M=M+1'     # Increment the stack pointer
            ])
        elif command == 'not':
            assembly_code.extend([
                '// not',
                '@SP',
                'M=M-1',
                'A=M',
                'M=!M',     # Perform bitwise NOT on the value in place
                '@SP',
                'M=M+1'
            ])

        self.output_file.write('\n'.join(assembly_code) + '\n')

    def write_push_pop(self, command, segment, index):
        """Writes the assembly code for C_PUSH or C_POP commands."""
        assembly_code = []
        if command == CommandType.C_PUSH:
            if segment == 'constant':
                assembly_code.extend([
                    f'// push constant {index}',
                    f'@{index}',    # Load the constant into the A register
                    'D=A',          # Store the constant in the D register
                    '@SP',          # Get the stack pointer address
                    'A=M',          # Set A to the top of the stack
                    'M=D',          # Write the constant to the top of the 
                                    # stack
                    '@SP',          # Get the stack pointer address
                    'M=M+1'         # Increment the stack pointer
                ])
            elif segment in self.segment_registers:
                base_reg = self.segment_registers.get(segment)
                assembly_code.extend([
                    f'// push {segment} {index}',
                    f'@{index}',
                    'D=A',          # D = index
                    f'@{base_reg}',
                    'A=M',          # A = base address of segment
                    'A=D+A',        # A = address + index
                    'D=M',          # D = value at RAM[address + index]
                    '@SP',
                    'A=M',
                    'M=D',          # *SP = D
                    '@SP',
                    'M=M+1'         # SP++
                ])
            elif segment == 'temp':
                target_addr = 5 + index
                assembly_code.extend([
                    f'// push temp {index}',
                    f'@{target_addr}',
                    'D=M',          # D = value at RAM[5 + index]
                    '@SP',
                    'A=M',
                    'M=D',
                    '@SP',
                    'M=M+1'
                ])
        elif command == CommandType.C_POP:
            assembly_code.extend(self._write_pop(segment, index))

        self.output_file.write('\n'.join(assembly_code) + '\n')

    def close(self):
        """Closes the output file."""
        self.output_file.close()

