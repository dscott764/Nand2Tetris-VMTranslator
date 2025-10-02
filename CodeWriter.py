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
        self.file_name = ''

    def write_sp_init(self):
        """Writes assembly to initialize SP=256 (no Sys.init call)."""
        assembly_code = [
            '// Bootstrap Code',
            '@256',
            'D=A',
            '@SP',
            'M=D'
        ]
        self.output_file.write('\n'.join(assembly_code) + '\n')

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

    def _write_static_push(self, index):
        """Helper to write code for pushing from static segment."""
        return [
            f'// push static {index}',
            f'@{self.file_name}.{index}',
            'D=M',              # D = static value
            '@SP',
            'A=M',
            'M=D',              # *SP = D
            '@SP',
            'M=M+1'             # SP++
        ]

    def _write_static_pop(self, index):
        """Helper to write code for popping to static segment."""
        return [
            f'// pop static {index}',
            '@SP',
            'M=M-1',            # SP--
            'A=M',
            'D=M',              # D = *SP (value to pop)
            f'@{self.file_name}.{index}',
            'M=D'               # static = D
        ]

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

    def _write_comparison_op(self, jump_mnemonic):
        """Helper for eq, lt, gt, which share the same structure."""
        true_label = f'{jump_mnemonic}_TRUE_{self.label_counter}'
        end_label = f'{jump_mnemonic}_END_{self.label_counter}'
        self.label_counter += 1

        return [
            f'// {jump_mnemonic.lower()}',
            '@SP',
            'M=M-1',
            'A=M',
            'D=M',
            '@SP',
            'M=M-1',
            'A=M',
            'D=M-D',
            f'@{true_label}',
            f'D;{jump_mnemonic}',
            'D=0',
            f'@{end_label}',
            '0;JMP',
            f'({true_label})',
            'D=-1',
            f'({end_label})',
            '@SP',
            'A=M',
            'M=D',
            '@SP',
            'M=M+1'
        ]

    def write_arithmetic(self, command):
        """Writes the assembly code for the given arithmetic command."""
        assembly_code = []
        if command in ['add', 'sub', 'and', 'or']:
            op_map = {
                'add': 'M=D+M', 'sub': 'M=M-D', 'and': 'M=D&M', 'or': 'M=D|M'
            }
            assembly_code.extend(self._write_binary_op(op_map[command]))
        elif command == 'eq':
            assembly_code.extend(self._write_comparison_op('JEQ'))
        elif command == 'lt':
            assembly_code.extend(self._write_comparison_op('JLT'))
        elif command == 'gt':
            assembly_code.extend(self._write_comparison_op('JGT'))
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

    def _write_pointer_push(self, index):
        """Helper to write code for pushing from pointer segment."""
        # 3 for pointer 0 (THIS), 4 for pointer 1 (THAT)
        ptr_addr = 3 + index

        return [
            f'// push pointer {index}',
            f'@{ptr_addr}',
            'D=M',
            '@SP',
            'A=M',
            'M=D',              # D = * (3 + index)
            '@SP',
            'M=M+1'             # SP++
        ]

    def _write_pointer_pop(self, index):
        """Helper to write code for popping to pointer segment."""
        # 3 for pointer 0 (THIS), 4 for pointer 1 (THAT)
        ptr_addr = 3 + index

        return [
            f'//pop pointer {index}',
            '@SP',
            'M=M-1',            # SP--
            'A=M',
            'D=M',              # D = *SP (value to pop)
            f'@{ptr_addr}',
            'M=D'               # *(3 + index) = D
        ]

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
            elif segment == 'static':
                assembly_code.extend(self._write_static_push(index))
            elif segment == 'pointer':
                assembly_code.extend(self._write_pointer_push(index))
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
            if segment == 'pointer':
                assembly_code.extend(self._write_pointer_pop(index))
            elif segment == 'static':
                assembly_code.extend(self._write_static_pop(index))
            else:
                assembly_code.extend(self._write_pop(segment, index))

        self.output_file.write('\n'.join(assembly_code) + '\n')

    def write_label(self, symbol):
        """Writes the assembly code for a C_LABEL command."""
        self.output_file.write(f'\n({symbol})\n')

    def write_if(self, label):
        """Writes the assembly code for a C_IF command."""
        assembly_code = [
            f'// if-goto {label}',
            '@SP',
            'M=M-1',    # Pop value from stack
            'A=M',
            'D=M',      # D = popped value
            f'@{label}',
            'D;JNE'     # Jump to label if D is not equal to 0
        ]
        self.output_file.write('\n'.join(assembly_code) + '\n')

    def write_goto(self, label):
        """Writes the assembly code for a C_GOTO command."""
        assembly_code = [
            f'// goto {label}',
            f'@{label}',
            '0;JMP'
        ]
        self.output_file.write('\n'.join(assembly_code) + '\n')

    def write_function(self, function_name, n_vars):
        """Writes assembly for the 'function' command."""
        assembly_code = [
            f'({function_name})'    # Create the function label
        ]
        # Push 0 n_vars times
        for _ in range(n_vars):
            assembly_code.extend([
                '@SP',
                'A=M',
                'M=0',
                '@SP',
                'M=M+1'
            ])
        self.output_file.write('\n'.join(assembly_code) + '\n')

    def write_return(self):
        """Writes assembly for the 'return' command."""
        assembly_code = [
            '// return',
            '@LCL',
            'D=M',
            '@R13',             # R13 (endFrame) = LCL
            'M=D',

            '@5',
            'A=D-A',
            'D=M',
            '@R14',             # R14 (retAddr) = *(endFrame - 5)
            'M=D',

            '// *ARG = pop()',
            '@SP',
            'M=M-1',
            'A=M',
            'D=M',
            '@ARG',
            'A=M',
            'M=D',

            '// SP = ARG + 1',
            '@ARG',
            'D=M+1',
            '@SP',
            'M=D',

            '// THAT = *(endFrame - 1)',
            '@R13', 'D=M', '@1', 'A=D-A', 'D=M', '@THAT', 'M=D',
            '// THIS = *(endFrame - 2)',
            '@R13', 'D=M', '@2', 'A=D-A', 'D=M', '@THIS', 'M=D',
            '// ARG = *(endFrame - 3)',
            '@R13', 'D=M', '@3', 'A=D-A', 'D=M', '@ARG', 'M=D',
            '// LCL = *(endFrame - 4)',
            '@R13', 'D=M', '@4', 'A=D-A', 'D=M', '@LCL', 'M=D',

            '// goto retAddr',
            '@R14',
            'A=M',
            '0;JMP'
        ]
        self.output_file.write('\n'.join(assembly_code) + '\n')

    def write_call(self, function_name, n_args):
        """Writes assembly code for the 'call' command."""
        return_label = f'{function_name}$ret.{self.label_counter}'
        self.label_counter += 1

        assembly_code = [
            f'// call {function_name} {n_args}',
            # --- Push return-address ---
            f'@{return_label}',
            'D=A',
            '@SP', 'A=M', 'M=D',
            '@SP', 'M=M+1',
            # --- Push LCL, ARG, THIS, THAT ---
            '@LCL', 'D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1',
            '@ARG', 'D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1',
            '@THIS', 'D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1',
            '@THAT', 'D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1',
            # --- Reposition ARG = SP - 5 - n_args ---
            '@SP', 'D=M',
            '@5', 'D=D-A',
            f'@{n_args}', 'D=D-A',
            '@ARG', 'M=D',
            # --- Reposition LCL = SP ---
            '@SP', 'D=M',
            '@LCL', 'M=D',
            # --- Goto function ---
            f'@{function_name}',
            '0;JMP',
            # --- Declare return-address label ---
            f'({return_label})'
        ]
        self.output_file.write('\n'.join(assembly_code) + '\n')

    def set_file_name(self, file_name):
        """
        Informs the code writer that the translation of a new VM file has
        started.
        """
        self.file_name = file_name

    def close(self):
        """Closes the output file."""
        self.output_file.close()
