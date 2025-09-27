import sys
import os
from Parser import Parser, CommandType
from CodeWriter import CodeWriter


def main():
    if len(sys.argv) < 2:
        print('Usage: python VMTranslator.py <path_to_file.vm>')
        sys.exit(1)

    input_path = sys.argv[1]
    base_name = os.path.splitext(input_path)[0]
    output_path = base_name + '.asm'

    try:
        parser = Parser(input_path)
        code_writer = CodeWriter(output_path, base_name)

        while parser.has_more_commands():
            parser.advance()
            cmd_type = parser.command_type()

            if cmd_type == CommandType.C_ARITHMETIC:
                command = parser.arg1()
                code_writer.write_arithmetic(command)
            elif cmd_type in [CommandType.C_PUSH, CommandType.C_POP]:
                segment = parser.arg1()
                index = parser.arg2()
                code_writer.write_push_pop(cmd_type, segment, index)

        code_writer.close()
        print(f'Translation finished.  Output written to {output_path}')
    except FileNotFoundError:
        print(f'Error: File not found at \'{input_path}\'')
        sys.exit(1)
    except ValueError as e:
        print(f'Translation Error: {e}')
        sys.exit(1)

if __name__ == '__main__':
    main()

