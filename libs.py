# read
def read_program(filename):
    f = open(filename, 'r')
    program = f.read()
    f.close()
    return program



