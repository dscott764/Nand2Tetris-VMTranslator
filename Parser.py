from enum import Enum, auto


class CommandType(Enum):
    C_ARITHMETIC = auto()
    C_PUSH = auto()
    C_POP = auto()
    C_LABEL = auto()
    C_GOTO = auto()
    C_IF = auto()
    C_FUNCTION = auto()
    C_RETURN = auto()
    C_CALL = auto()


class Parser:
    ARITHMETIC_COMMANDS = {
        'add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not'
    }

    def __init__(self, file_path):
        """
        Opens the input file, cleans it of all comments and whitespace, and
        stores a list of pure commands.
        """
        with open(file_path, 'r') as file:
            raw_lines = file.readlines()

        cleaned_lines = []
        for line in raw_lines:
            cleaned_line = line.split('//')[0].strip()

            if cleaned_line:
                cleaned_lines.append(cleaned_line)

        self.lines = cleaned_lines
        self.current_line_index = -1
        self.current_command = ''

    def has_more_commands(self):
        """Returns True if there are any more commands in the input."""
        return self.current_line_index < len(self.lines) - 1

    def advance(self):
        """
        Reads the next command from the input and makes it the current command.
        """
        self.current_line_index += 1
        self.current_command = self.lines[self.current_line_index]

    def command_type(self):
        """Returns the type of the current VM command."""
        first_word = self.current_command.split()[0]

        if first_word in self.ARITHMETIC_COMMANDS:
            return CommandType.C_ARITHMETIC
        elif first_word == 'push':
            return CommandType.C_PUSH
        elif first_word == 'pop':
            return CommandType.C_POP
        elif first_word == 'label':
            return CommandType.C_LABEL
        elif first_word == 'if-goto':
            return CommandType.C_IF
        elif first_word == 'goto':
            return CommandType.C_GOTO
        elif first_word == 'function':
            return CommandType.C_FUNCTION
        elif first_word == 'return':
            return CommandType.C_RETURN
        elif first_word == 'call':
            return CommandType.C_CALL
        else:
            raise ValueError(
                f'Unknown command type for: {self.current_command}')

    def arg1(self):
        """
        Returns the first argument of the current command.
        For C_ARITHMETIC, the command itself is returned.
        """
        cmd_type = self.command_type()

        if cmd_type == CommandType.C_ARITHMETIC:
            # For arithmetic commands, return the command itself (e.g., 'add')
            return self.current_command.split()[0]
        elif cmd_type != CommandType.C_RETURN:
            # For most other commands, return the second word
            return self.current_command.split()[1]

    def arg2(self):
        """
        Returns the second argument of the current command.
        Should only be called for C_PUSH, C_POP, C_FUNCTION, or C_CALL.
        """
        # The second argument is the third word in the command, returned as an
        # int
        return int(self.current_command.split()[2])
