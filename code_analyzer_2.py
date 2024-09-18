import re


class CodeAnalyzer:
    semicolon_outside_comment = re.compile(r'^[^#]*;')
    already_after_hash = re.compile(r'#.*#')
    in_quotes = re.compile(r'[\'"].*;.*[\'"]')
    less_than_two_spaces = re.compile(r'[^#\s]\s?#')
    any_todo = re.compile(r'todo', re.IGNORECASE)
    correct_todo = re.compile(r'\stodo:\s', re.IGNORECASE)
    todo_outside_comment = re.compile(r'^[^#]*todo', re.IGNORECASE)

    def __init__(self, file):
        self.file = file
        self.lines = self.get_lines()
        self.style_list = []

    def get_lines(self):
        with open(self.file, 'r') as f:
            return f.readlines()

    def length(self):
        for i, line in enumerate(self.lines, 1):
            if len(line) > 79:
                self.style_list.append(f'Line {i}: S001 Too long')

    def indentation(self):
        for i, line in enumerate(self.lines, 1):
            indent = len(line) - len(line.lstrip(' '))
            if indent % 4 != 0:
                self.style_list.append(
                    f'Line {i}: S002 Indentation is not a multiple of four')

    def semicolon(self):
        for i, line in enumerate(self.lines, 1):
            if self.semicolon_outside_comment.search(line) and not self.in_quotes.search(line):
                self.style_list.append(f'Line {i}: S003 Unnecessary semicolon')

    def inline_comment_space(self):
        for i, line in enumerate(self.lines, 1):
            if self.less_than_two_spaces.search(line) and not self.already_after_hash.search(line):
                self.style_list.append(
                    f'Line {i}: S004 At least two spaces required before inline comments')

    def todo(self):
        for i, line in enumerate(self.lines, 1):
            if self.any_todo.search(line) and not self.correct_todo.search(
                    line) and not self.todo_outside_comment.search(line):
                self.style_list.append(f'Line {i}: S005 TODO found')

    def blank_lines(self):
        count = 0
        for i, line in enumerate(self.lines, 1):
            if line.strip() == '':
                count += 1
            elif count > 2:
                self.style_list.append(
                    f'Line {i}: S006 More than two blank lines used before this line')
                count = 0
            else:
                count = 0


def main():
    check = CodeAnalyzer(input())
    check.length()
    check.indentation()
    check.semicolon()
    check.inline_comment_space()
    check.todo()
    check.blank_lines()
    check.style_list.sort(key=lambda x: int(x.split()[1].strip(':')))
    for line in check.style_list:
        print(line)


main()