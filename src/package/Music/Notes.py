class Note:
    def __init__(self, representation, measure=0, beat=0, length=0):
        # encode alternate representations
        # base is FLAT, alt is SHARP
        self.representation = representation
        self.measure = measure
        self.beat = beat
        self.length = length  # length is the denom of a note, e.g. length of 4 is a quarter note (as 1/4 = quarter)

        if self.representation[-1] == 'b':
            # get previous note to 'sharp'
            note_index = NOTES_REPRESENTATIONS.index(self.representation)
            prev_note = NOTES_REPRESENTATIONS[note_index-1]
            self.alt_representation = f'{prev_note}#'
        else:
            self.alt_representation = None

        return

    def __str__(self):
        if self.alt_representation is None:
            return self.representation
        else:
            return f'{self.alt_representation}/{self.representation}'

def construct_notes():
    notes = []
    for note_rep in NOTES_REPRESENTATIONS:
        new_note = Note(note_rep)
        notes.append(new_note)
    return notes


NOTES_REPRESENTATIONS = ['A', 'Bb', 'B', 'C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab']
NOTES_REPRESENTATIONS_SHARPS = ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']

NOTE_TRANSLATIONS = {
    'Fb': 'E',
    'Cb': 'B'
}

# list of keys for which we use FLATS in the key signature/notation
# all others use SHARP
FLAT_KEYS = ['Ab', 'Bb', 'Db', 'Eb', 'Gb', 'F']

NOTES = construct_notes()




# just testing here for now
if __name__ == '__main__':
    # make sure that NOTES are ordered and represented properly
    for note in NOTES:
        print(note, end=' ')
