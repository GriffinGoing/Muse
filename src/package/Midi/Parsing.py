"""
https://www.twilio.com/blog/working-with-midi-data-in-python-using-midoss
"""

from mido import MidiFile, MetaMessage

class MidiParser:
    def __init__(self, path):
        self.path = path
        self.midi = self.parse_midi(self.path)

        self.tracks = []
        for track in self.midi.tracks:
            self.parse_track(track)


    def parse_midi(self, path):
        midi = MidiFile(path, clip=True)
        print(midi)

        return midi

    def parse_track(self, track):
        # dict for tracking note indices (e.g. active notes have an entry here)
        note_states = {}
        notes = []

        print(self.midi.ticks_per_beat)
        print(track)

        for message in track:
            if isinstance(message, MetaMessage):
                continue
            print(message.__dict__)

            # deduce measure

            # if this is a new note, create and place in dict

            # if this is the end of a note, complete the note object using the index found in the dict

        return

# TESTING HERE FOR NOW
if __name__ == '__main__':
    #midi_parser = MidiParser('./Samples/C-Scale.mid')
    print("SkipMeasure ---------------------------")
    midi_parser = MidiParser('./Samples/SkipMeasure.mid')

    print("SkipMeasureBuffer ---------------------------")
    midi_parser = MidiParser('./Samples/SkipMeasureBuffer.mid')

    print("SkipMeasureBuffer2 ---------------------------")
    midi_parser = MidiParser('./Samples/SkipMeasureBuffer2.mid')

    print("SkipMeasureBuffer3 ---------------------------")
    midi_parser = MidiParser('./Samples/SkipMeasureBuffer3.mid')

    midi_parser.save('./saved_smb3.mid')
