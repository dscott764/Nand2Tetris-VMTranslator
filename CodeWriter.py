from Parser import CommandType


class CodeWriter:
    def __init__(self, output_file_path):
        """
        Opens the output file for writing and prepares for code generation.
        """
        self.output_file = open(output_file_path, 'w')

    def write_arithmetic(self, command):
        """Writes the assembly code for the given arithmetic command."""
        assembly_code = []
        if command == 'add':
            assembly_code.extend([
                '// add',
                '@SP',      # Decrement stack pointer
                'M=M-1',
                'A=M',      # Get address of y (top value)
                'D=M',      # Store y in D register
                '@SP',      # Decrement stack pointer again
                'M=M-1',
                'A=M',      # Get address of x (new top value)
                'M=D+M',    # Store x+y in M (at address of x)
                '@SP',      # Increment stack pointer
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
        elif command == CommandType.C_POP:
            pass

        self.output_file.write('\n'.join(assembly_code) + '\n')

    def close(self):
        """Closes the output file."""
        self.output_file.close()

