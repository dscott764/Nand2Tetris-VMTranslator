import sys
import os
from Parser import Parser, CommandType
from CodeWriter import CodeWriter


def main():
    if len(sys.argv) < 2:
        print('Usage: python VMTranslator.py <path_to_file.vm>')
        sys.exit(1)

    input_path = sys.argv[1]
    base_name_with_path = os.path.splitext(input_path)[0]
    output_path = base_name_with_path + '.asm'
    file_name_for_static = os.path.basename(base_name_with_path)

    try:
        parser = Parser(input_path)
        code_writer = CodeWriter(output_path, file_name_for_static)

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
            elif cmd_type == CommandType.C_LABEL:
                label = parser.arg1()
                code_writer.write_label(label)
            elif cmd_type == CommandType.C_IF:
                label = parser.arg1()
                code_writer.write_if(label)
            elif cmd_type == CommandType.C_GOTO:
                label = parser.arg1()
                code_writer.write_goto(label)
            elif cmd_type == CommandType.C_FUNCTION:
                function_name = parser.arg1()
                n_vars = parser.arg2()
                code_writer.write_function(function_name, n_vars)
            elif cmd_type == CommandType.C_RETURN:
                code_writer.write_return()

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

