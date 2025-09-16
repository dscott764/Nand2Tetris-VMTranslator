class Parser:
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

    def hasMoreCommands(self):
        """Returns True if there are any more commands in the input."""
        return self.current_line_index < len(self.lines) - 1

    def advance(self):
        """
        Reads the next command from the input and makes it the current command.
        """
        self.current_line_index += 1
        self.current_command = self.lines[self.current_line_index]
        print(self.current_command.strip())

