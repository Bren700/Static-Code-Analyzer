import sys
import os
import re
import ast


class CodeAnalyzer:

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

    def path_iterator(self):
        for py_path in self.py_paths:
            self.analyser(py_path)

    def get_lines(self, f_path):
        with open(f_path, 'r') as f:
            return f.readlines()

    def analyser(self, f_path):
        alerts = []
        count = 0
        lines = self.get_lines(f_path)
        for i, line in enumerate(lines, 1):
            if construct := re.search(r'(class|def)\s\s+', line):
                alerts.append(f"{f_path}: Line {i}: S007 Too many spaces after '{construct.group(1)}'")

            if class_name := re.search(r'(class\s+)([a-z]+)', line):
                alerts.append(f"{f_path}: Line {i}: S008 Class name '{class_name.group(2)}' should use CamelCase")

            if function_name := re.search(r'(def\s+)([A-Z]+[A-z_0-9]*)', line):
                alerts.append(
                    f"{f_path}: Line {i}: S009 Function name '{function_name.group(2)}' should use snake_case")

            if len(line) > 79:
                alerts.append(f'{f_path}: Line {i}: S001 Too long')

            indent = len(line) - len(line.lstrip(' '))
            if indent % 4 != 0:
                alerts.append(
                    f'{f_path}: Line {i}: S002 Indentation is not a multiple of four')

            if re.search(r'^[^#]*;', line) and not re.search(r'[\'"].*;.*[\'"]', line):
                alerts.append(f'{f_path}: Line {i}: S003 Unnecessary semicolon')

            if re.search(r'[^#\s]\s?#', line) and not re.search(r'#.*#', line):
                alerts.append(
                    f'{f_path}: Line {i}: S004 At least two spaces required before inline comments')

            if re.search(r'todo', line, re.IGNORECASE) and not re.search(
                    r'\stodo:\s', line, re.IGNORECASE) and not re.search(
                r'^[^#]*todo', line, re.IGNORECASE):
                alerts.append(f'{f_path}: Line {i}: S005 TODO found')

            if line.strip() == '':
                count += 1
            elif count > 2:
                alerts.append(
                    f'{f_path}: Line {i}: S006 More than two blank lines used before this line')
                count = 0
            else:
                count = 0

        with open(f_path, 'r') as f:
            tree = ast.parse(f.read())

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    for arg in node.args.args:
                        arg_name = arg.arg
                        if not re.search(r'^[a-z_][a-z0-9_]*$', arg_name):
                            alerts.append(f"{f_path}: Line {
                            arg.lineno}: S010 Argument name '{arg_name}' should be snake_case")

                    mutable_types = (ast.List, ast.Dict, ast.Set)
                    for default in node.args.defaults:
                        if isinstance(default, mutable_types):
                            alerts.append(f"{f_path}: Line {arg.lineno}: S012 Default argument value is mutable")

                    for n in ast.walk(node):
                        if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store):
                            variable_name = n.id
                            if not re.search(r'^[a-z_][a-z0-9_]*$', variable_name):
                                alerts.append(f"{f_path}: Line {n.lineno}: S011 Variable '{
                                variable_name}' in function should be snake_case")

        alerts.sort(key=lambda x: int(x.split('Line')[1].split(':')[0]))
        for line in alerts:
            self.files_alerts.append(line)


def main():
    examine = CodeAnalyzer(sys.argv[1])
    examine.path_iterator()
    for line in examine.files_alerts:
        print(line)


main()