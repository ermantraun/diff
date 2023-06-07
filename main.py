from os import path
import pickle

def decode_delta_file_to_dict(file_name):
    with open(file_name + '.pickle', 'rb') as delta_record:        
        delta = pickle.load(delta_record)
    return delta


def encode_dict_to_delta_file(delta, file_name):
    with open(file_name + '.pickle', 'wb') as delta_record:
     pickle.dump(delta, delta_record)

def get_subtrahend(minuend, delta):
    subtrahend = [list(line) for line in minuend.split('\n')]
    remainder_strings = delta.pop('end')

    for line in delta.items():
        remainder_symbols = line[1].pop(-1)
        for ranges in line[1]:
            subtrahend[line[0]][ranges[0]:ranges[1] + 1] = ranges[2]

        subtrahend[line[0]] = subtrahend[line[0]] + list(remainder_symbols[1]) if remainder_symbols[0] == '+' else subtrahend[line[0]][:remainder_symbols[1] + 1]
    if remainder_strings[0] == '+':
        subtrahend.extend([list(i) for i in remainder_strings[1]])
    elif remainder_strings[0] == '-':
        subtrahend = subtrahend[:remainder_strings[1]]
    print(delta)
    return '\n'.join(''.join(i) for i in subtrahend)

def get_delta(minuend:str, subtrahend:str):
    minuend, subtrahend = minuend.split('\n'), subtrahend.split('\n')
    smallest_line_amount = min(minuend, subtrahend, key=len)
    delta = dict()
    different_symbols_count = 0
    for line in range(len(smallest_line_amount)):
        smallest_line = min(minuend[line], subtrahend[line], key=len)
        current_range = None
        for column in range(len(smallest_line)):
            symbol_1, symbol_2 = minuend[line][column], subtrahend[line][column]
            if symbol_1 != symbol_2:
                different_symbols_count += 1
                if current_range is None:
                    current_range = [column, column, symbol_2]
                else:
                    current_range[1] = column
                    current_range[2] += symbol_2
            else:
                if current_range is not None:
                    if line not in delta:
                        delta[line] = []
                    delta[line].append(current_range)
                    current_range = None

        if current_range is not None:
            if line not in delta:
                delta[line] = []
            delta[line].append(current_range)
            current_range = None

        if line in delta:
            if smallest_line == subtrahend[line]:
                delta[line].append(['-', len(smallest_line)])
            else:
                delta[line].append(['+', subtrahend[line][len(smallest_line):]])

    if len(minuend) > len(subtrahend):
        delta['end'] = ['-', len(subtrahend)]
    elif len(minuend) == len(subtrahend):
        delta['end'] = [None]
    else:
        delta['end'] = ['+', subtrahend[len(minuend):]]
    
    return delta, different_symbols_count

def write_version(file_header, file_contents):
    name, format_ = file_header.split('.')
    versions_file_name = name + '_versions.' + format_
    if path.isfile(versions_file_name):
        versions_file = open(versions_file_name).read()
        versions = versions_file.split(';')[:-1]
        min_diff_version = None
        for version in versions:
            parent_presence = version.find(':')
            version_number = version[:parent_presence]
            if version_number[-1] == '-':
                version_file = open(version[parent_presence + 1:]).read()
                delta = get_delta(version_file, file_contents)
                print(get_subtrahend(version_file, delta[0]))
                if min_diff_version is None:
                    min_diff_version = version_number, delta
                else:
                    min_diff_version = min(min_diff_version, (version_number, delta), key= lambda x: x[1][1])
        

            
    else:
        open(versions_file_name, 'w').write('1-:' + file_header + ';')                                     
        open(file_header, 'w').write(file_contents)


def get_version(file_header, version):
    pass

