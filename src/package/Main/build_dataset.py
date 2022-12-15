import sys

from ..Data import Read


def main():
    if len(sys.argv) != 2:
        print('Data directory is required as a CLI argument')
        return

    data_dir = sys.argv[1]

    # see McGill-Billboard dataset for file structure
    for dir in data_dir:
        metadata, sections = read_chords_from_file(f'{data_dir}/{dir}/salami_chords.txt')

    return

if __name__ == '__main__':
    main()
