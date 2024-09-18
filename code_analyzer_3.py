import re
import os
import sys


class CodeAnalyzer:
    semicolon_outside_comment = re.compile(r'^[^#]*;')
    already_after_hash = re.compile(r'#.*#')
    in_quotes = re.compile(r'[\'"].*;.*[\'"]')
    less_than_two_spaces = re.compile(r'[^#\s]\s?#')
    any_todo = re.compile(r'todo', re.IGNORECASE)
    correct_todo = re.compile(r'\stodo:\s', re.IGNORECASE)
    todo_outside_comment = re.compile(r'^[^#]*todo', re.IGNORECASE)

    def __init__(self, path):
        self.path = os.path.normpath(path)
        self.py_paths = self.get_paths()
        self.files_alerts = []

    def get_paths(self):
        paths_lst = []
        if self.path.endswith(".py"):
            paths_lst.append(self.path)

        else:
            for root, dirs, files in os.walk(self.path, topdown=False):
                for file in files:
                    if file.endswith(".py"):
                        paths_lst.append(os.path.join(root, file))
        return paths_lst

    def get_lines(self, file_path):
        with open(file_path, 'r') as f:
            return f.readlines()

    def path_iterator(self):
        for py_path in self.py_paths:
            self.analyser(py_path)

    def analyser(self, file_path):
        alerts = []
        count = 0
        lines = self.get_lines(file_path)
        for i, line in enumerate(lines, 1):
            if len(line) > 79:
                alerts.append(f'{file_path}: Line {i}: S001 Too long')

            indent = len(line) - len(line.lstrip(' '))
            if indent % 4 != 0:
                alerts.append(
                    f'{file_path}: Line {i}: S002 Indentation is not a multiple of four')

            if self.semicolon_outside_comment.search(line) and not self.in_quotes.search(line):
                alerts.append(f'{file_path}: Line {i}: S003 Unnecessary semicolon')

            if self.less_than_two_spaces.search(line) and not self.already_after_hash.search(line):
                alerts.append(
                    f'{file_path}: Line {i}: S004 At least two spaces required before inline comments')

            if self.any_todo.search(line) and not self.correct_todo.search(
                    line) and not self.todo_outside_comment.search(line):
                alerts.append(f'{file_path}: Line {i}: S005 TODO found')

            if line.strip() == '':
                count += 1
            elif count > 2:
                alerts.append(
                    f'{file_path}: Line {i}: S006 More than two blank lines used before this line')
                count = 0
            else:
                count = 0
        alerts.sort(key=lambda x: int(x.split('Line')[1].split(':')[0]))
        for line in alerts:
            self.files_alerts.append(line)


def main():
    examine = CodeAnalyzer(sys.argv[1])
    examine.path_iterator()
    for line in examine.files_alerts:
        print(line)


main()