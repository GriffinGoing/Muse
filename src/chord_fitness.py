"""
Must be in PonyGE fitness directory
"""

import json
import re
import random
import os
from datetime import datetime
import csv

# from .....Muse.src.package.Music.Chord import Chord

from .base_ff_classes.base_ff import base_ff

"""
CURRENT FITNESS EVALUATIONS (probabilistic):
    - Start and penultimate chords (full chord)
    - Note (individual)
    - Note-Quality pairs
    - Note-Quality-Extension sets
    - Note->Note movements
    - Note:Qual->Note:Qual

"""

"""
- dynamically adjust weights based on global affect on fitness?
- how can we stay in key? minor key chords (like bIII) are rewarded for being in a progression based off of the Imin


TO DO: 
    - add root movement generation and probabilities (from root to root, requires distance/interval heuristic from package.Music)
    - selection mechanics?
"""


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


DEFAULT_CONFIG = {
    "penalty_exponent": 2,
    "seed": True,
    "output_dir": '../../../run_results'

}

TEST_SEED = {
    'start': "Imaj",
    # 'penultimate': "Vdom7",
    'end': "Imaj",
    "seed_percentage": 1.0,
}

"""
Breaks down the string of a chord into it's individual pieces
e.g. note, root, quality, extensions, alterations, inversions
"""


def parse_chord(chord):
    # regex
    alterations_re = re.compile(r"\(.+\)")
    qualities_re = re.compile(r"maj|min|dim|hdim|aug|sus|dom|pow")
    root_re = re.compile(r"/[#|b]*\d{1}")

    # get roman numeral
    # print(chord)
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


class chord_fitness(base_ff):
    def __init__(self):
        super().__init__()

        # read chord fitness probability dict from JSON
        probs_file = open('./fitness_probs.json')
        self.probs = json.load(probs_file)

        # read JSON config or use defaults if not found
        try:
            config_file = open('./fitness_config.json')
            self.config = json.load(config_file)
        except FileNotFoundError as e:
            self.show_warning(f'FITNESS CONFIG WARNING: Fitness config file not found, using defaults.')
            self.config = DEFAULT_CONFIG

        # check if seeding is enabled and if so, init seed data
        if self.config['seed']:
            try:
                self.seed = self.config['seed_data']
            except KeyError as e:
                self.show_warning(f'FITNESS CONFIG WARNING: No seed data found, using testing defaults.')
                self.seed = TEST_SEED

        # check if parent output dir exists, and make/open
        dir_path = self.config['output_dir']
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)

        # make output dir for *this* run, write config, open .csv file for result logging
        now = datetime.now()
        dir_path = f'{dir_path}/results_{now.strftime("%m-%d-%Y_%H:%M:%S")}'
        os.mkdir(dir_path)
        json_config_out = open(f'{dir_path}/config.json', 'w')
        json.dump(self.config, json_config_out)
        self.output_file = open(f'{dir_path}/progressions.csv', 'w')
        self.output_writer = csv.writer(self.output_file)

        # write CSV headers
        self.output_writer.writerow(['generation', 'fitness', 'progression'])

        self.dump_first = True

        self.curr_generation = -1

    def show_warning(self, text):
        print(f'{bcolors.WARNING}{text}{bcolors.ENDC}')
        return

    def scoring_function(self, probability, weight=1):
        exponent = self.config['penalty_exponent']
        result = (1 - probability) ** exponent
        result = result * weight
        return result

    def evaluate(self, ind, **kwargs):
        if ind.name == 0:
            self.curr_generation = self.curr_generation + 1

        chords_orig = ind.phenotype
        # break chords down into array
        chords = chords_orig.split(':')
        # print(chords)

        # if seeding is enabled, swap out chords in all matching places
        if (self.config['seed']):
            if random.uniform(0, 1) < self.seed['seed_percentage']:
                if 'start' in self.seed.keys():
                    chords[0] = self.seed['start']
                if 'end' in self.seed.keys():
                    chords[-1] = self.seed['end']
                if 'penultimate' in self.seed.keys():
                    chords[-2] = self.seed['penultimate']

        fitness = 0

        # get note probabilities, note-quality pair probabilities, and extension probs (given note and quality)
        for chord in chords:
            note, quality, extension = parse_chord(chord)
            fitness = fitness + self.scoring_function(self.probs['note'][note], weight=3)
            fitness = fitness + self.scoring_function(self.probs['quality'][note][quality], weight=2)

            try:
                fitness = fitness + self.scoring_function(self.probs['extension'][note][quality][extension])
            except KeyError as e:
                fitness = fitness + self.scoring_function(0)
                # print(f'Found no EXTENSION key for {note}-{quality}-{extension}: {e}')

            # fitness = fitness + (1 - self.probs['note'][note])

        # get note->note probabilities (movement)
        for i in range(0, len(chords)):
            # skip if there is no "next" chord e.g. i+1 index
            if i + 1 >= len(chords):
                continue

            chord_a = chords[i]
            chord_b = chords[i + 1]
            note_a, qual_a, ext_a = parse_chord(chord_a)
            note_b, qual_b, ext_b = parse_chord(chord_b)
            try:
                fitness = fitness + self.scoring_function(self.probs['movement'][f'{note_a}-{note_b}'], weight=2)
                # fitness = fitness + self.probs['movement'][f'{note_a}-{note_b}']
                # fitness = fitness + (1 - self.probs['movement'][f'{note_a}-{note_b}'])
            except KeyError as e:
                print(f'No probability data for movement {note_a}-{note_b}')

        # get note:qual -> note:qual probabiltities (movement w/ quality)

        # get probabilities for start chords (first and last chord, since last chord is start of new progression)
        start_chord = chords[0]
        fitness = fitness + self.scoring_function(self.probs['start_chord'][start_chord], weight=1)
        # fitness = fitness + (1 - self.probs['start_chord'][start_chord])
        start_chord = chords[-1]
        fitness = fitness + self.scoring_function(self.probs['start_chord'][start_chord], weight=1)
        # fitness = fitness + (1 - self.probs['start_chord'][start_chord])

        # get probability for penultimate (second to last) chord
        penultimate_chord = chords[-2]
        fitness = fitness + self.scoring_function(self.probs['penultimate_chord'][penultimate_chord])
        # fitness = fitness + (1 - self.probs['penultimate_chord'][penultimate_chord])

        # print(f'{fitness} Chords: {chords_orig}')
        delimiter = ' '
        print(f'{self.curr_generation} {ind.name} {fitness} Chords: {delimiter.join(chords)}')
        self.output_writer.writerow([self.curr_generation, fitness, delimiter.join(chords)])

        if self.dump_first:
            print(ind.__dict__)
            # jstr = json.dumps(ind)
            # json.dump(jstr, self.output_file)
            self.dump_first = False

        # bonus points for length of progression!!!
        # fitness = fitness + len(chords)

        return fitness

