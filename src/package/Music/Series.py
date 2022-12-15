from Notes import Note, NOTES

"""
Models a series of notes (e.g. a melody, harmonic line, etc)

Can opt to support 2d arrays (which would allow modeling chords/multiple notes at a  time)
"""
class Series:
    def __init__(self, starting_note, intervals, key=None):
        self.key = key
        self.intervals = intervals
        self.notes = create_notes(starting_note, intervals)

        return

    def __str__(self):
        # sanity check, printing resulting series
        str_notes = []
        for note in self.notes:
            str_notes.append(note.representation)
        return ' '.join(str_notes)


"""
Create an array of notes from a set of intervals
"""
def create_notes(starting_note, intervals, key=None):
    series_notes = []

    # convert starting note to note object
    starting_note = Note(starting_note)

    print(starting_note)

    # find index of starting note
    curr_note_index = 0
    for i in range(0, len(NOTES)):
        if NOTES[i].representation == starting_note.representation:
            curr_note_index = i
            break

    # build series by iterating over the intervals and modifying the current note index within the NOTES array
    series_notes.append(starting_note)
    for interval in intervals:
        curr_note_index = curr_note_index + interval
        print(curr_note_index)
        if curr_note_index < 0:
            curr_note_index = curr_note_index + 12
        if curr_note_index >= len(NOTES):
            curr_note_index = curr_note_index - len(NOTES)
        series_notes.append(NOTES[curr_note_index])


    return series_notes

if __name__ == '__main__':
    c_scale = Series('C', [2, 2, 1, 2, 2, 2, 1])
    print(c_scale)
