import json
import sys

"""
counts are the frequency of occurrence, so it's important to note that while
we're using counts for the fitness function (to make probabilities),
we're actually using the keys of those counts to construct a grammar to draw from
"""
TEST_COUNTS = {
    'note': {
        '1': 1,
        '2': 1,
        '3': 1,
        '4': 1,
        '5': 1,
        '6': 1,
        '7': 1,
    }
}


"""
TO ADD: resolving sequences (cadences), 
"""

def build_grammar(output_filepath, count_dict):
    # open output file
    grammar_file = open(output_filepath, 'w')

    for category in count_dict:
        symbols = " | ".join(count_dict[category].keys())
        grammar_file.write(f'<{category}> ::= {symbols}\n')

    return


def main():
    json_file = sys.argv[1]
    output_file = sys.argv[2]

    # load json from input
    json_file = open(json_file)
    data = json.load(json_file)
    build_grammar(output_file, data)
    return

# testing here as usual
if __name__ == '__main__':
    #build_grammar('./test_grammar_build.pybnf', TEST_COUNTS)
    main()