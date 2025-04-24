import sys

MEM_SIZE = 2048 # words

def main():
    path = sys.argv[1]
    with open(path, 'r+') as file:
        lines = file.readlines()
        current_line_count = len(lines)

        if current_line_count < MEM_SIZE:
            lines_to_add =  MEM_SIZE - current_line_count
            for _ in range(lines_to_add):
                lines.append('00000000\n')

            file.seek(0)
            file.writelines(lines)
            file.truncate()

if __name__ == '__main__':
    main()
