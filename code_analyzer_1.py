
with open(input(), 'r') as file:
    for i, line in enumerate(file, 1):
        if len(line) > 79:
            print(f'Line {i}: S001 Too long')

