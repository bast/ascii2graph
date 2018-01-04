import re
from collections import defaultdict
from .errors import throw_error


def get_character(line_number, character_position, text):
    '''
    Returns character in position (line_number, character_position).
    If there is no character (if the position is "outside" the text),
    function returns None.
    '''
    if line_number < 0 or character_position < 0:
        return None
    lines = text.split('\n')
    try:
        return lines[line_number][character_position]
    except IndexError:
        return None


def test_get_character():
    text = '''all work and no play
all work and no
all work and
all work
all'''
    # just outside top left corner
    assert get_character(-1, -1, text) is None
    # top left
    assert get_character(0, 0, text) == 'a'
    # first line, second character
    assert get_character(0, 1, text) == 'l'
    # second line, last character
    assert get_character(1, 14, text) == 'o'
    # last line, second character
    assert get_character(4, 2, text) == 'l'
    # second line, outside
    assert get_character(1, 15, text) is None
    # non-existent line
    assert get_character(-1, 14, text) is None


def get_connecting_coordinates(line_number,
                               character_position,
                               text,
                               follow_coordinate1=True,
                               follow_coordinate2=True):

    character = get_character(line_number, character_position, text)
    if character is None:
        throw_error('character is None in get_connecting_coordinates; weird')

    if character == '-':
        c1 = (line_number, character_position - 1)
        c2 = (line_number, character_position + 1)
    elif character == '/':
        c1 = (line_number + 1, character_position - 1)
        c2 = (line_number - 1, character_position + 1)
    elif character == '\\':
        c1 = (line_number - 1, character_position - 1)
        c2 = (line_number + 1, character_position + 1)
    elif character == '|':
        c1 = (line_number - 1, character_position)
        c2 = (line_number + 1, character_position)
    else:
        throw_error('unexpected character in get_connecting_coordinates: {0}'.format(character))

    if follow_coordinate1:
        if get_character(c1[0], c1[1], text) in ['-', '/', '\\', '|']:
            c1, _ = get_connecting_coordinates(line_number=c1[0],
                                               character_position=c1[1],
                                               text=text,
                                               follow_coordinate2=False)
    if follow_coordinate2:
        if get_character(c2[0], c2[1], text) in ['-', '/', '\\', '|']:
            _, c2 = get_connecting_coordinates(line_number=c2[0],
                                               character_position=c2[1],
                                               text=text,
                                               follow_coordinate1=False)

    return c1, c2


def test_get_connecting_coordinates():
    text = r'''
    a-b---eee
       \   \
     x  c---[d12]
     |  |
     x oh
      \|
       o
       |
       b'''
    assert get_connecting_coordinates(2, 7, text) == ((1, 6), (3, 8))
    assert get_connecting_coordinates(1, 7, text) == ((1, 6), (1, 10))
    assert get_connecting_coordinates(1, 8, text) == ((1, 6), (1, 10))
    assert get_connecting_coordinates(1, 9, text) == ((1, 6), (1, 10))
    assert get_connecting_coordinates(3, 10, text) == ((3, 8), (3, 12))


def locate_all_words(text):
    # list of line numbers for each character
    line_numbers = []
    for i, line in enumerate(text.split('\n')):
        for character in line:
            line_numbers.append(i)

    # list of character positions for each character
    character_positions = []
    for line in text.split('\n'):
        for i, _ in enumerate(line):
            character_positions.append(i)

    text_one_line = ''.join(text.split('\n'))

    words = {}

    offset = 0
    # we find everything that is not - = / \ |
    for word in re.findall(r'[^-/\|\\\s+]+', text):
        # we found the word
        i = text_one_line.index(word)

        # create dictionary entries mapping coordinates to the word
        for j, _ in enumerate(word):
            words[(line_numbers[offset + i], character_positions[offset + i + j])] = (line_numbers[offset + i],
                                                                                      character_positions[offset + i],
                                                                                      word)

        # we discard everything up to the word
        text_one_line = text_one_line[i + len(word):]
        offset += i + len(word)

    return words


def test_locate_all_words():
    text = r'''
    a-b---eee
       \   \
     x  c---[d12]
     |  |
     x oh
      \|
       o
       |
       b'''
    assert locate_all_words(text) == {(1, 4): (1, 4, 'a'),
                                      (1, 6): (1, 6, 'b'),
                                      (1, 10): (1, 10, 'eee'),
                                      (1, 11): (1, 10, 'eee'),
                                      (1, 12): (1, 10, 'eee'),
                                      (3, 5): (3, 5, 'x'),
                                      (3, 8): (3, 8, 'c'),
                                      (3, 12): (3, 12, '[d12]'),
                                      (3, 13): (3, 12, '[d12]'),
                                      (3, 14): (3, 12, '[d12]'),
                                      (3, 15): (3, 12, '[d12]'),
                                      (3, 16): (3, 12, '[d12]'),
                                      (5, 5): (5, 5, 'x'),
                                      (5, 7): (5, 7, 'oh'),
                                      (5, 8): (5, 7, 'oh'),
                                      (7, 7): (7, 7, 'o'),
                                      (9, 7): (9, 7, 'b')}


def graph(text):

    words = locate_all_words(text)

    coordinate_tuples = []
    lines = text.split('\n')
    for line_number, line in enumerate(lines):
        for character_position, _ in enumerate(line):
            if lines[line_number][character_position] in ['-', '/', '\\', '|']:
                c = get_connecting_coordinates(line_number,
                                               character_position,
                                               text)
                coordinate_tuples.append(c)

    # we remove duplicate tuples that come from "long" connections
    coordinate_tuples = set(coordinate_tuples)

    graph = defaultdict(list)
    for (s, e) in coordinate_tuples:
        if not words[e] in graph[words[s]]:
            graph[words[s]].append(words[e])
        if not words[s] in graph[words[e]]:
            graph[words[e]].append(words[s])
    return graph


def test_graph():
    text = r'''
    a-b---eee
       \   \
     x  c---[d12]
     |  |
     x oh
      \|
       o
       |
       b'''
    reference = {(3, 8, 'c'): [(3, 12, '[d12]'), (5, 7, 'oh'), (1, 6, 'b')],
                 (3, 12, '[d12]'): [(3, 8, 'c'), (1, 10, 'eee')],
                 (1, 6, 'b'): [(1, 10, 'eee'), (1, 4, 'a'), (3, 8, 'c')],
                 (1, 10, 'eee'): [(1, 6, 'b'), (3, 12, '[d12]')],
                 (5, 7, 'oh'): [(3, 8, 'c'), (7, 7, 'o')],
                 (7, 7, 'o'): [(5, 7, 'oh'), (5, 5, 'x'), (9, 7, 'b')],
                 (3, 5, 'x'): [(5, 5, 'x')],
                 (5, 5, 'x'): [(3, 5, 'x'), (7, 7, 'o')],
                 (1, 4, 'a'): [(1, 6, 'b')],
                 (9, 7, 'b'): [(7, 7, 'o')]}
    result = graph(text)
    for node in result:
        assert set(result[node]) == set(reference[node])

    text = r'''
    a--boo
    |   |   x
    |   |  /
    c---d-e
        | |
        f-g'''
    reference = {(1, 4, 'a'): [(4, 4, 'c'), (1, 7, 'boo')],
                 (4, 4, 'c'): [(1, 4, 'a'), (4, 8, 'd')],
                 (4, 8, 'd'): [(4, 4, 'c'), (4, 10, 'e'), (1, 7, 'boo'), (6, 8, 'f')],
                 (4, 10, 'e'): [(2, 12, 'x'), (4, 8, 'd'), (6, 10, 'g')],
                 (2, 12, 'x'): [(4, 10, 'e')],
                 (6, 8, 'f'): [(6, 10, 'g'), (4, 8, 'd')],
                 (6, 10, 'g'): [(6, 8, 'f'), (4, 10, 'e')],
                 (1, 7, 'boo'): [(4, 8, 'd'), (1, 4, 'a')]}
    result = graph(text)
    for node in result:
        assert set(result[node]) == set(reference[node])
