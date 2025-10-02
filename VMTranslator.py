import sys
import os
from Parser import Parser, CommandType
from CodeWriter import CodeWriter


def main():
    if len(sys.argv) < 2:
        print('Usage: python VMTranslator.py <path_to_file_or_directory>')
        sys.exit(1)

    input_path = sys.argv[1]
    files_to_translate = []

    if os.path.isdir(input_path):
        # Input is a directory
        # Sanitize path to remove any trailing slashes
        input_path = os.path.normpath(input_path)
        dir_name = os.path.basename(input_path)
        output_path = os.path.join(input_path, dir_name + '.asm')

        # Find all .vm files in the directory
        for file in os.listdir(input_path):
            if file.endswith('.vm'):
                files_to_translate.append(os.path.join(input_path, file))
    elif os.path.isfile(input_path):
        # Input is a single file
        if not input_path.endswith('.vm'):
            raise ValueError('Input file must be a .vm file.')
        base_name = os.path.splitext(input_path)[0]
        output_path = base_name + '.asm'
        files_to_translate.append(input_path)
    else:
        print(
            f'Error: Input path \'{input_path}\' '
            'is not a valid file or directory.')
        sys.exit(1)

    # --- Main Translation Process ---
    try:
        # Create one CodeWriter for the single output file
        code_writer = CodeWriter(output_path)

        # Always init SP for directories
        code_writer.write_sp_init()

        # Call Sys.init only if Sys.vm is present
        has_sys = any(os.path.basename(vm_file).lower() == 'sys.vm'
                      for vm_file in files_to_translate)
        if has_sys:
            code_writer.write_call('Sys.init', 0)

        # Loop through each .vm file
        for vm_file_path in files_to_translate:
            base_name = os.path.splitext(os.path.basename(vm_file_path))[0]
            # Set the filename for the static segment
            code_writer.set_file_name(base_name)

            parser = Parser(vm_file_path)
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
                elif cmd_type == CommandType.C_CALL:
                    function_name = parser.arg1()
                    n_args = parser.arg2()
                    code_writer.write_call(function_name, n_args)

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
