
with open('c_module.c', 'rb') as f:
    data = f.read()
    print('Position 27:', repr(data[27]))
    print('Context:', repr(data[20:35]))
