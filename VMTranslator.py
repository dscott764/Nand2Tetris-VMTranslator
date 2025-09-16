import sys
from Parser import Parser


def main():
    # Check if a file path was provided on the command line
    if len(sys.argv) < 2:
        print('Usage: python VMTranslator.py <path_to_file.vm>')
        sys.exit(1)

    file_path = sys.argv[1]

    try:
        parser = Parser(file_path)

        while parser.hasMoreCommands():
            parser.advance()
    except FileNotFoundError:
        print(f'Error: File not found at "{file_path}"')
        sys.exit(1)

if __name__ == '__main__':
    main()

