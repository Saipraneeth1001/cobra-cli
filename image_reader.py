import time

def read_image():
    reader = open('cobra-text.txt', 'r')
    lines = reader.readlines()

    for line in lines:
        print(line, end='')
        time.sleep(0.2)

def file_reader():
    reader = open('equities.txt', 'r')
    lines = [line.rstrip('\n') for line in reader.readlines()]
    return lines
    
        
