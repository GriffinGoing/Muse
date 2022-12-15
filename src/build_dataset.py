import json
import os
import re
import sys

from package.Data import Read
from package.Music.Chord import toRomanNumeral

CHORD_QUALITIES = ['maj', 'min', 'dom', 'aug', 'dim', 'hdim', 'sus', 'pow']

def write_counts(counts, output_file):
    output_file = open(output_file, 'w')
    json.dump(counts, output_file, indent=4)
    return

def build_counts(songs):
    # init counts dict
    counts = {}

    counts['note'] = {} # the number of times a given roman numeral (note relative to tonic) occurs in the progression
    counts['movement'] = {} # the number of times we see one note go to another e.g. <note> -> <note>

    """
    qualities are organized by their parity with a given note (roman numeral form), e.g.
    counts['quality']['VII']['dim'] returns a probability that the VII chord has a quality of dim,
    and thus would correlate to the proportion of VII chord that had a quality of dim at time of examination
    """
    counts['quality'] = {}

    """
    start and penultimate chords to open and close the sequence
    """
    counts['start_chord'] = {}
    counts['penultimate_chord'] = {}
    counts['extension'] = {}

    # add resolving movements (cadences, e.g. V-I, V-vi, etc.)

    count_notes(songs, counts)
    count_movements(songs, counts)
    count_qualities(songs, counts)
    count_start_chords(songs, counts)
    count_penultimate_chords(songs, counts)
    count_extensions(songs, counts)

    print(counts)
    #print(counts['start_chord'].keys())
    return counts

"""
probability of *this* extension given *this* chord and quality
"""
def count_extensions(songs, counts):
    # init dictionary key for each note and quality
    for note in counts['note']:
        counts['extension'][note] = {}
        for quality in CHORD_QUALITIES:
            counts['extension'][note][quality] = {}

    # perform note:quality:ext counts
    for song in songs:
        for section in songs[song]['sections']:
            # print(section)
            for chord in songs[song]['sections'][section]:
                try:
                    note = chord.note
                    quality = chord.quality
                    ext = chord.extension
                    counts['extension'][note][quality][ext] = counts['extension'][note][quality][ext] + 1

                except KeyError as e:
                    counts['extension'][note][quality][ext] = 1
                    #print(f'Failed quality key increment on {chord.note} -> {chord.quality}')
                    #input()
                except AttributeError as e:
                    print(f'Failed count iteration on chord {chord}: {e}')

    # normalize counts: get total -> value = (count) / (total count) e.g. proportion of total (given prior)
    for note in counts['extension']:
        for quality in counts['extension'][note]:
            total = 0
            for ext in counts['extension'][note][quality]:
                total = total + counts['extension'][note][quality][ext]
            for ext in counts['extension'][note][quality]:
                counts['extension'][note][quality][ext] = counts['extension'][note][quality][ext] / total

    return


def count_start_chords(songs, counts):
    # perform raw note counts
    for song in songs:
        for section in songs[song]['sections']:
            # print(section)

            section = songs[song]['sections'][section]

            # check if there is a chord to grab
            if len(section) < 1:
                continue

            chord = str(section[0])
            # if time signature, bunny hop
            if chord[0] == '(':
                chord = str(section[1])
            #print(chord)

            try:
                counts['start_chord'][chord] = counts['start_chord'][chord] + 1
            except KeyError as e:
                counts['start_chord'][chord] = 1
            except AttributeError as e:
                print(f'Failed count iteration on chord {chord}: {e}')
            """
            for chord in songs[song]['sections'][section]:
                try:
                    counts['note'][chord.note] = counts['note'][chord.note] + 1
                    # print(chord)
                    # print(chord.note)
                except KeyError as e:
                    counts['note'][chord.note] = 1
                except AttributeError as e:
                    print(f'Failed count iteration on chord {chord}: {e}')
            """

    # normalize counts: get total -> value = (count) / (total count) e.g. proportion of total
    total = 0
    for chord in counts['start_chord']:
        total = total + counts['start_chord'][chord]
    for chord in counts['start_chord']:
        counts['start_chord'][chord] = counts['start_chord'][chord] / total

    return


def count_penultimate_chords(songs, counts):
    # perform raw note counts
    for song in songs:
        for section in songs[song]['sections']:
            # print(section)

            section = songs[song]['sections'][section]

            # check if there is a chord to grab
            if len(section) < 1:
                continue

            chord = str(section[-1])
            # if time signature, bunny hop
            #if chord[0] == '(':
            #    chord = str(section[-2])
            # print(chord)

            try:
                counts['penultimate_chord'][chord] = counts['penultimate_chord'][chord] + 1
            except KeyError as e:
                counts['penultimate_chord'][chord] = 1
            except AttributeError as e:
                print(f'Failed count iteration on chord {chord}: {e}')
            """
            for chord in songs[song]['sections'][section]:
                try:
                    counts['note'][chord.note] = counts['note'][chord.note] + 1
                    # print(chord)
                    # print(chord.note)
                except KeyError as e:
                    counts['note'][chord.note] = 1
                except AttributeError as e:
                    print(f'Failed count iteration on chord {chord}: {e}')
            """

    # normalize counts: get total -> value = (count) / (total count) e.g. proportion of total
    total = 0
    for chord in counts['penultimate_chord']:
        total = total + counts['penultimate_chord'][chord]
    for chord in counts['penultimate_chord']:
        counts['penultimate_chord'][chord] = counts['penultimate_chord'][chord] / total
    return


def count_qualities(songs, counts):
    # init dictionary key for each note and quality
    for note in counts['note']:
        counts['quality'][note] = {}
        for quality in CHORD_QUALITIES:
            counts['quality'][note][quality] = 0

    # perform note:quality counts
    for song in songs:
        for section in songs[song]['sections']:
            # print(section)
            for chord in songs[song]['sections'][section]:
                try:
                    note = chord.note
                    quality = chord.quality
                    counts['quality'][note][quality] = counts['quality'][note][quality] + 1

                except KeyError as e:
                    #counts['note'][chord.note] = 1
                    print(f'Failed quality key increment on {chord.note} -> {chord.quality}')
                    input()
                except AttributeError as e:
                    print(f'Failed count iteration on chord {chord}: {e}')

    # normalize counts: get total -> value = (count) / (total count) e.g. proportion of total
    for note in counts['quality']:
        total = 0
        for quality in counts['quality'][note]:
            total = total + counts['quality'][note][quality]
        for quality in counts['quality'][note]:
            counts['quality'][note][quality] = counts['quality'][note][quality] / total

    return

def count_movements(songs, counts):

    # get raw counts
    for song in songs:
        for section in songs[song]['sections']:
            #for chord in songs[song]['sections'][section]:
            for i in range(0, len(songs[song]['sections'][section])):
                # check that i+1 exists
                if i+1 >= len(songs[song]['sections'][section]):
                    continue

                # skip when object at index i is a string (is a time signature)
                if type(songs[song]['sections'][section][i]) is str:
                    continue

                # get details of movement
                try:

                    chord_a = songs[song]['sections'][section][i]
                    chord_b = songs[song]['sections'][section][i+1]

                    # if chord_b ends up being a time signature, leap over it to the next index
                    if type(chord_b) is str:
                        # check if i+2 exists
                        if i+2 < len(songs[song]['sections'][section]):
                            chord_b = songs[song]['sections'][section][i+2]
                        # need to add look-ahead logic because this keeps us from resolving progressions
                        else:
                            continue


                    note_a = chord_a.note
                    note_b = chord_b.note

                    counts['movement'][f'{note_a}-{note_b}'] = counts['movement'][f'{note_a}-{note_b}'] + 1
                except KeyError as e:
                    chord_a = songs[song]['sections'][section][i]
                    chord_b = songs[song]['sections'][section][i + 1]

                    # if chord_b ends up being a time signature, leap over it to the next index
                    if type(chord_b) is str:
                        chord_b = songs[song]['sections'][section][i + 2]

                    note_a = chord_a.note
                    note_b = chord_b.note

                    counts['movement'][f'{note_a}-{note_b}'] = 1
                except AttributeError as e:
                    note_a = songs[song]['sections'][section][i]
                    note_b = songs[song]['sections'][section][i+1]
                    print(f'Failed count iteration on chords {note_a}-{note_b} {type(note_a)}-{type(note_b)}: {e}')

    # normalize counts: get total -> value = (count) / (total count) e.g. proportion of total
    total = 0
    for movement in counts['movement']:
        total = total + counts['movement'][movement]
    for movement in counts['movement']:
        counts['movement'][movement] = counts['movement'][movement] / total

    return

def count_notes(songs, counts):

    # perform raw note counts
    for song in songs:
        for section in songs[song]['sections']:
            #print(section)
            for chord in songs[song]['sections'][section]:
                try:
                    counts['note'][chord.note] = counts['note'][chord.note] + 1
                    #print(chord)
                    #print(chord.note)
                except KeyError as e:
                    counts['note'][chord.note] = 1
                except AttributeError as e:
                    print(f'Failed count iteration on chord {chord}: {e}')

    # normalize counts: get total -> value = (count) / (total count) e.g. proportion of total
    total = 0
    for note in counts['note']:
        total = total + counts['note'][note]
    for note in counts['note']:
        counts['note'][note] = counts['note'][note] / total


    #print(counts)
    return

def main():
    if len(sys.argv) != 3:
        print('Data directory  and output json file are required as a CLI argumentss')
        return

    data_dir = sys.argv[1]

    # read all files
    # see McGill-Billboard dataset for file structure
    count = 0
    songs = {}
    for subdir in os.listdir(data_dir):
        # skip lousy OSX file stuff
        if subdir == '.DS_Store':
            continue

        metadata, sections = Read.read_chords_from_file(f'{data_dir}/{subdir}/salami_chords.txt')
        metadata['number'] = subdir
        songs[metadata['title']] = {}
        songs[metadata['title']]['metadata'] = metadata
        songs[metadata['title']]['sections'] = sections

        count = count + 1
    print()
    print(f'Read {count} files into dataset')

    # print the first song out just to check structure
    print(songs[songs.keys().__iter__().__next__()])

    """
    parse chords from every song loaded
    """
    time_change_re = re.compile(r"\(\d/\d\)")

    for song in songs:
        song_number = songs[song]['metadata']['number']
        key = songs[song]['metadata']['tonic']
        print(f'\rReading chords from #{song_number} - {song}', end='')
        #print(f'KEY: {key}')
        song = songs[song]
        for section in song['sections']:
            section = song['sections'][section]
            #for chord_string in section:
            for i in range(0, len(section)):
                chord_string = section[i]
                try:
                    # skip time changes
                    time_change = re.search(time_change_re, chord_string)
                    if time_change is not None:
                        start = time_change.span()[0]
                        end = time_change.span()[1]
                        #print(f'Found time change {chord_string[start:end]} . Skipping...')
                        continue

                    # skip uncaught characters
                    chord = Read.read_chord(chord_string, key)

                    # change this string to a chord object
                    section[i] = chord
                except Exception as e:
                    print(f'Failed on chord {chord_string} with exception {e}')
                    input()

    #print('Done reading chords')

    #print(songs)
    print(songs[songs.keys().__iter__().__next__()])



    counts = build_counts(songs)
    write_counts(counts, sys.argv[2])
    return

if __name__ == '__main__':
    main()
