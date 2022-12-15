#from Notes import Note, NOTES
import re

from .Notes import Note, NOTES, NOTES_REPRESENTATIONS, NOTES_REPRESENTATIONS_SHARPS, NOTE_TRANSLATIONS

# roots abstracted to any possible tone, in-key or otherwise
KEYLESS_ROOTS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

# roots allowing only in-key tones
KEY_ROOTS = [1, 2, 3, 4, 5, 6, 7]

# roman numeral representations of roots. all major, cast to minor as chord requires
ROMAN_NUMERALS = ['I', 'bII', 'II', 'bIII', 'III', 'IV', 'bV', 'V', 'bVI', 'VI', 'bVII', 'VII']

[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

# qualities and extensions
QUALITIES = ['', 'maj', 'min', 'sus', 'aug', 'dim'] # empty quality is fair game (e.g. in the case of dominant 7th chords)
EXTENSIONS = [5, 7, 9, 11, 13] # no extension is fair game (usually denotes triad, 5 is power chord)

# let's build/parse alterations from the dataset since the list could be pretty massive otherwise (or be vectorized in which case we have variable-length data types requiring variable-variable chromosomes)
ALTERATIONS = []

# returns number of semitones between two notes
def parseNumeric(note, key):

    # check for weird notes like 'Fb' and 'Cb' because idk some people hate being normal
    if note in NOTE_TRANSLATIONS.keys():
        note = NOTE_TRANSLATIONS[note]

    if key in NOTE_TRANSLATIONS.keys():
        key = NOTE_TRANSLATIONS[key]

    # cast notes to numbers on the "note line"
    try:
        note_index = NOTES_REPRESENTATIONS.index(note.capitalize())
    except:
        note_index = NOTES_REPRESENTATIONS_SHARPS.index(note.capitalize())

    try:
        key_index = NOTES_REPRESENTATIONS.index(key.capitalize())
    except:
        key_index = NOTES_REPRESENTATIONS_SHARPS.index(key.capitalize())


    #print(f'Math for note:key {note}:{key} got {note_index} - {key_index} = {note_index - key_index}')

    # return the number of semitones the note is from the key (tonic)
    return note_index - key_index

def toRomanNumeral(note, key):
    value = parseNumeric(note, key)
    #print(f'Relationship for {note} in the key of {key}: {ROMAN_NUMERALS[value]}')
    return ROMAN_NUMERALS[value]

class Chord:
    def __init__(self, note, quality, extension, root, alterations=None, key=None):
        self.note = note
        self.root = root
        self.quality = quality.lower()
        self.extension = extension

        # we may need to revisit typing here. Currently, everything is represented as a string.
        # this might make doing math/conversiond on certain chord attrs annoying later if we
        # dont type some of them
        #self.extension = int(extension)

        # represent alterations as a single string perhaps?
        self.alterations = alterations

        # if this is a sus chord the 4th/11 is not suspended, set it to sus4 by default
        if self.quality == 'sus' and self.extension != '4' and self.extension != '11' and self.extension != '13':
            #print(f'Found bad sus chord {self.quality}{self.extension}, modifying to sus4')
            self.extension = '4'

        return

    def std_print(self):
        if self.quality in ['maj', 'dom', 'aug', 'sus']:
            return f'{self.note}{self.quality}{self.extension}'
        else:
            return f'{self.note.lower()}{self.quality}{self.extension}'

    def __str__(self):
        return f'{self.note}{self.quality}{self.extension}'

    def pretty_print(self):
        print('--------------------')
        print(f'Note: {self.note}')
        print(f'Quality: {self.quality}')
        print(f'Ext: {self.extension}')
        print(f'Root: {self.root}')
        print(f'Alteration: {self.alterations}')
        print('--------------------')


# DEPRECATED - use read_chord from Data module
# assumes form '<note><maj|min|etc><ext>', e.g. assumes 3-letter
def parse_chord(chord):
    #ext_pattern = re.compile('[^a-z]+', re.IGNORECASE)

    root_end_index = 1

    # check for sharp or flat. not checking for double sharp/flat currently
    if chord[1] == '#' or chord[1] == 'b':
        root_end_index = 2

    root = chord[0:root_end_index]
    quality = chord[root_end_index:root_end_index+3]
    #extension = re.match(ext_pattern, chord)
    extension = chord[root_end_index+3:]

    new_chord = Chord(root, quality, extension)
    return new_chord

def test_parsing():
    chord = parse_chord("cmaj")
    print(chord)

    chord = parse_chord("cMAJ")
    print(chord)

    chord = parse_chord("cmaj7")
    print(chord)

    chord = parse_chord("cMAJ7")
    print(chord)

    chord = parse_chord("cmaj13")
    print(chord)

    chord = parse_chord("cMAJ13")
    print(chord)

    chord = parse_chord("Bb7")
    print(chord)

    chord = parse_chord("D#sus7")
    print(chord)
    return

if __name__ == '__main__':
    test_parsing()