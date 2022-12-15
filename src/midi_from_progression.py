"""
Adapted from the pychord example at https://github.com/yuma-m/pychord/blob/main/examples/pychord-midi.py
to take progressions as CLI arguments in roman-numeral form
"""


import pretty_midi
import sys
from pychord import Chord
import re
import pygame

NOTES_FROM_C = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
ROMAN_NUMERALS = ['I', 'bII', 'II', 'bIII', 'III', 'IV', 'bV', 'V', 'bVI', 'VI', 'bVII', 'VII']

def parse_chord(chord):
    # regex
    alterations_re = re.compile(r"\(.+\)")
    qualities_re = re.compile(r"maj|min|dim|hdim|aug|sus|dom|pow")
    root_re = re.compile(r"/[#|b]*\d{1}")

    # get roman numeral
    #print(chord)
    roman_re = re.compile(r"[b|#]*[IiVv]+", re.IGNORECASE)
    roman_match = re.search(roman_re, chord)
    start = roman_match.span()[0]
    end = roman_match.span()[1]
    note = chord[start:end]

    chord = chord.replace(note, '')

    # get quality
    quality_match = re.search(qualities_re, chord)
    start = quality_match.span()[0]
    end = quality_match.span()[1]
    quality = chord[start:end]
    chord = chord.replace(quality, '')

    # extract/remove root if chord is an inversion
    # init root to note as default
    root = ''
    root_match = re.search(root_re, chord)
    if root_match != None:
        start = root_match.span()[0]
        end = root_match.span()[1]
        root = chord[start:end]
        chord = chord.replace(root, '')
        root = root.replace('/', '')

    # extract alterations if they exist
    alterations = ''
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


    return note, quality, extension


def create_midi(chords):
    midi_data = pretty_midi.PrettyMIDI()
    piano_program = pretty_midi.instrument_name_to_program('Acoustic Grand Piano')
    piano = pretty_midi.Instrument(program=piano_program)
    length = 1
    for n, chord in enumerate(chords):
        for note_name in chord.components_with_pitch(root_pitch=4):
            note_number = pretty_midi.note_name_to_number(note_name)
            note = pretty_midi.Note(velocity=100, pitch=note_number, start=n * length, end=(n + 1) * length)
            piano.notes.append(note)
    midi_data.instruments.append(piano)
    midi_data.write('chord.mid')


def main():
    chords = []
    if len(sys.argv) == 2:
        chords = sys.argv[1]
        chords = chords.split(':')
    else:
        chords = sys.argv[1:]

    prepped_chords = []
    for chord in chords:
        note, quality, ext = parse_chord(chord)
        # convert note from roman numeral to note in key of C
        roman_index = ROMAN_NUMERALS.index(note)
        note_in_c = NOTES_FROM_C[roman_index]

        # remove qualities that pychord does not support
        if quality == 'dom':
            quality = ''
        if quality == 'hdim':
            quality = 'dim'
        prepped_chords.append(f'{note_in_c}{quality}{ext}')


    #print(f'Chords: {chords}')
    #print(f'Prepped Chords: {prepped_chords}')

    chords = [Chord(c) for c in prepped_chords]
    create_midi(chords)

    #print(f'Playing music..')
    pygame.init()
    pygame.mixer.music.load('chord.mid')
    pygame.mixer.music.play()

    wait_for = pygame.time.get_ticks()
    while pygame.mixer.music.get_busy():
        pygame.time.wait(wait_for)


if __name__ == '__main__':
    main()


