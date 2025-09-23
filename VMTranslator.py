import sys
from Parser import Parser, CommandType


def main():
    COMMANDS_WITH_ARG2 = {
        CommandType.C_PUSH,
        CommandType.C_POP,
        CommandType.C_FUNCTION,
        CommandType.C_CALL
    }

    # Check if a file path was provided on the command line
    if len(sys.argv) < 2:
        print('Usage: python VMTranslator.py <path_to_file.vm>')
        sys.exit(1)

    file_path = sys.argv[1]

    try:
        parser = Parser(file_path)
        print(f'{"Command":<25} | {"Type":<25} | {"Arg1":<15} | {"Arg2"}')
        print('-' * 75)

        while parser.hasMoreCommands():
            parser.advance()
            cmd_type = parser.commandType()

            # Print Command and Type
            output_line = f'{parser.current_command:<25} | {str(cmd_type):<25}'
            print(output_line, end='')

            # Print Arg1
            # C_RETURN is the only command without any arguments
            if cmd_type != CommandType.C_RETURN:
                arg1 = parser.arg1()
                print(f' | {arg1:<15}', end='')

            # Print Arg2 only for specific command types
            if cmd_type in COMMANDS_WITH_ARG2:
                arg2 = parser.arg2()
                print(f' | {arg2}')
            else:
                print()
    except FileNotFoundError:
        print(f'Error: File not found at "{file_path}"')
        sys.exit(1)

if __name__ == '__main__':
    main()

