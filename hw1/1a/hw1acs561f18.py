input_file = 'input.txt'
output_file = 'output.txt'

lines = [line.rstrip('\n') for line in open(input_file)]
pairs = [(line.split(',')[0], line.split(',')[-1]) for line in lines]
output = []

for pair in pairs:
    status = pair[-1]
    location = pair[0]
    if status == 'Dirty':
        output.append('Suck')
    elif location == 'A':
        output.append('Right')
    elif location == 'B':
        output.append('Left')

with open(output_file, 'w') as f:
    f.write('\n'.join(output))
