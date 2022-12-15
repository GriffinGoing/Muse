import re
from ..Music import Chord

FORM_INDICATOR_LETTERS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']


def read_chords_from_file(filepath):
    print(f'\rReading file at {filepath}', end='')
    f = open(filepath, 'r')

    # get title
    line = f.readline()
    words = line.split()
    title = words[words.index('title:')+1:]
    title = ' '.join(title)

    # get artist
    line = f.readline()
    words = line.split()
    artist = words[words.index('artist:') + 1:]
    artist = ' '.join(artist)

    # quick fix for TONIC and METRE order sometime being switched
    metre = None
    tonic = None
    for i in range(0, 2):
        line = f.readline()
        words = line.split()
        if 'metre:' in words:
            metre = words[words.index('metre:') + 1:]
            metre = ' '.join(metre)
        elif 'tonic:' in words:
            tonic = words[words.index('tonic:') + 1:]
            tonic = ' '.join(tonic)


    # assign metadata
    metadata = {}
    metadata['title'] = title
    metadata['artist'] = artist
    metadata['metre'] = metre
    metadata['tonic'] = tonic

    section_counts = {}
    sections = {}
    current_chords = []
    current_section = ''
    for line in f:
        words = line.split()
        #print(words)

        # skip empty lines
        if len(words) < 1:
            continue

        """
        If we find a form indicator, we know that we're entering a new section of the song
        and we should therefore set the current chord progression to an empty array
        Additionally, we should save the current chords under the previous section name
        
        Note: the form indicator (A, B, C, etc) is always at index 1 if it exists
        """
        if words[1].replace(',', '') in FORM_INDICATOR_LETTERS:
            # if we currently in a section, save it
            if current_section != '':
                # this is a quick-fix for skipping (well, not saving) repeated sections
                # l as N indicates verbatim repeated section
                if 'N' not in current_chords:
                    # increment the count for the current section (allows us to save sections separately
                    try:
                        section_counts[current_section] = section_counts[current_section] + 1
                    except KeyError as e:
                        section_counts[current_section] = 1

                    # save current list of chords under the key <section name><count>
                    sections[f'{current_section}_{section_counts[current_section]}'] = current_chords

            current_section = words[2].replace(',', '')
            current_chords = []
            # print(f'Indicator found. Moving to progression for {current_section}')

        """
        Gather the chords by getting the first and last index of the pipe operator
        This is probably more work than we need to do, but it's also an extra
        layer of safety
        """

        try:
            first_pipe_index = words.index('|') + 1
        except ValueError as e:
            continue

        # assume last index. if it is not the last index, it is the second-last
        second_pipe_index = -1
        if words[second_pipe_index] != '|':
            second_pipe_index = -2

        chord_subset = words[first_pipe_index:second_pipe_index]

        for chord in chord_subset:
            # ignore pipes. currently ignoring dots and * (rhythm indicators)
            # should add time changes here if we really want to ignore them
            # could add x(number) as well if we want to ignore repeats
            # also ignores '->' (not sure what this is for yet)
            if chord.replace(',', '') != '|' and chord != '.' and chord != '*' and chord[0] != 'x' and chord[0] != '-':
                current_chords.append(chord)

        #print(chord_subset)
        #print(current_chords)
    return metadata, sections


"""
Breaks down the string of a chord into it's individual pieces
e.g. note, root, quality, extensions, alterations, inversions
"""
def read_chord(chord, key):
    #print(chord)

    key_change = re.compile(r"\([A-Ga-g]{1}[#|b]*\)")
    key_change_match = re.search(key_change, chord)

    if key_change_match != None:
        start = key_change_match.span()[0]
        end = key_change_match.span()[1]
        print(f'WARNING: key change found: {chord[start:end]}')
        input()


    original = chord
    note_re = re.compile(r"[A-Ga-g]{1}[#|b]*")
    alterations_re = re.compile(r"\(.+\)")
    qualities_re = re.compile(r"maj|min|dim|hdim|aug|sus")
    root_re = re.compile(r"/[#|b]*\d{1}")

    """ old version of note extraction, non regex
    # extract and remove note from chord
    chord = chord.split(':')
    note = chord[0]
    chord = chord[1]
    """

    # remove separators
    chord = chord.replace(':', '')

    #remove padding
    chord = chord.replace(' ', '')
    chord = chord.strip()

    # extract and remove note
    note = None
    note_match = re.search(note_re, chord)
    if note_match != None:
        start = note_match.span()[0]
        end = note_match.span()[1]
        note = chord[start:end]
        chord = chord.replace(note, '')
    else:
        print(f'Found no note match for chord {original}')

    # extract and remove quality if it is specified
    quality = None
    quality_match = re.search(qualities_re, chord)
    if quality_match != None:
        start = quality_match.span()[0]
        end = quality_match.span()[1]
        quality = chord[start:end]
        chord = chord.replace(quality, '')
    """
    else:
        print(f'WARNING: found no quality for chord {original}')
    """

    # extract/remove root if chord is an inversion
    # init root to note as default
    root = 1
    root_match = re.search(root_re, chord)
    if root_match != None:
        start = root_match.span()[0]
        end = root_match.span()[1]
        root = chord[start:end]
        chord = chord.replace(root, '')
        root = root.replace('/', '')

    # extract alterations if they exist
    alterations = None
    alter_match = re.search(alterations_re, chord)
    if alter_match != None:
        start = alter_match.span()[0]
        end = alter_match.span()[1]
        alterations = chord[start:end]
        chord = chord.replace(alterations, '')


    # in theory, if we have parsed out all other parts of the chord,
    # only the extension remains
    extension = chord

    # check for unset attributes and set according to other data found

    # if quality was unset, it's either dom or pow (power)
    # we can discern based on the extension
    if quality is None:
        if extension == '5':
            quality = 'pow'
        else:
            quality = 'dom'

    """
    Scrapping this because odd non-integer extensions might occur and I don't 
    foresee a need to alter these in a way that they would require a numeric typing
    
    
    # if extension was set, parse it to an int. If not, set to None
    if extension != '':
        extension = int(extension)
    else:
        extension = None
    """

    """
    print('--------------------')
    print(original)
    print(f'Note: {note}')
    print(f'Quality: {quality}')
    print(f'Ext: {extension}')
    print(f'Root: {root}')
    print(f'Alteration: {alterations}')
    print('--------------------')
    """
    #print(f'Parsed Chord: {original} : note={note}, quality={quality}, extension={extension}, root={root}, alt={alterations}')

    # convert note to roman numeral
    note = Chord.toRomanNumeral(note, key)
    parsed_chord = Chord.Chord(note=note, quality=quality, extension=extension, root=root, alterations=alterations)
    return parsed_chord


# as always, testing here
if __name__ == '__main__':
    #sections = read_chords_from_file('./McGill-Billboard/0003/salami_chords.txt')
    metadata, sections = read_chords_from_file('./McGill-Billboard/0004/salami_chords.txt')
    print(metadata)
    print(sections)

    read_chord(sections['intro_1'][1])
    read_chord(sections['verse_1'][2])
    read_chord(sections['bridge_1'][0])
    read_chord('C5')
