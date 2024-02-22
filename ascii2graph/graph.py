import re
from collections import defaultdict
from .errors import throw_error


def get_angle(c1, c2):
    assert c1 != c2
    if c1[0] < c2[0]:
        if c1[1] < c2[1]:
            return 135
        elif c1[1] == c2[1]:
            return 180
        elif c1[1] > c2[1]:
            return 225
    elif c1[0] == c2[0]:
        if c1[1] < c2[1]:
            return 90
        else:
            return 270
    elif c1[0] > c2[0]:
        if c1[1] < c2[1]:
            return 45
        elif c1[1] == c2[1]:
            return 0
        elif c1[1] > c2[1]:
            return 315


def get_character(line_number, character_position, text):
    """
    Returns character in position (line_number, character_position).
    If there is no character (if the position is "outside" the text),
    function returns None.
    """
    if line_number < 0 or character_position < 0:
        return None
    lines = text.split("\n")
    try:
        return lines[line_number][character_position]
    except IndexError:
        return None


def test_get_character():
    text = """all work and no play
all work and no
all work and
all work
all"""
    # just outside top left corner
    assert get_character(-1, -1, text) is None
    # top left
    assert get_character(0, 0, text) == "a"
    # first line, second character
    assert get_character(0, 1, text) == "l"
    # second line, last character
    assert get_character(1, 14, text) == "o"
    # last line, second character
    assert get_character(4, 2, text) == "l"
    # second line, outside
    assert get_character(1, 15, text) is None
    # non-existent line
    assert get_character(-1, 14, text) is None


def get_connecting_coordinates(
    line_number,
    character_position,
    text,
    follow_coordinate1=True,
    follow_coordinate2=True,
):
    character = get_character(line_number, character_position, text)
    if character is None:
        throw_error("character is None in get_connecting_coordinates; weird")

    if character == "-":
        c1 = (
            line_number,
            character_position - 1,
            False,
        )  # <-- True/False tells us whether this is an arrowhead
        c2 = (line_number, character_position + 1, False)
    elif character == ">":
        c1 = (line_number, character_position - 1, False)
        c2 = (line_number, character_position + 1, True)
    elif character == "<":
        c1 = (line_number, character_position - 1, True)
        c2 = (line_number, character_position + 1, False)
    elif character == "/":
        c1 = (line_number + 1, character_position - 1, False)
        c2 = (line_number - 1, character_position + 1, False)
    elif character == "\\":
        c1 = (line_number - 1, character_position - 1, False)
        c2 = (line_number + 1, character_position + 1, False)
    elif character == "|":
        c1 = (line_number - 1, character_position, False)
        c2 = (line_number + 1, character_position, False)
    elif character == "^":
        c1 = (line_number - 1, character_position, True)
        c2 = (line_number + 1, character_position, False)
    elif character == "v":
        c1 = (line_number - 1, character_position, False)
        c2 = (line_number + 1, character_position, True)
    else:
        throw_error(
            "unexpected character in get_connecting_coordinates: {0}".format(character)
        )

    if follow_coordinate1:
        if get_character(c1[0], c1[1], text) in [
            "-",
            "|",
            "/",
            "\\",
            "v",
            "^",
            "<",
            ">",
        ]:
            c1, _ = get_connecting_coordinates(
                line_number=c1[0],
                character_position=c1[1],
                text=text,
                follow_coordinate2=False,
            )
    if follow_coordinate2:
        if get_character(c2[0], c2[1], text) in [
            "-",
            "|",
            "/",
            "\\",
            "v",
            "^",
            "<",
            ">",
        ]:
            _, c2 = get_connecting_coordinates(
                line_number=c2[0],
                character_position=c2[1],
                text=text,
                follow_coordinate1=False,
            )

    return c1, c2


def test_get_connecting_coordinates():
    text = r"""
    a-b---eee
       \   \
     x  c<--[d12]
     |  ^
     v  |
     x oh
      \|
       o
       |
       b"""
    assert get_connecting_coordinates(2, 7, text) == ((1, 6, False), (3, 8, False))
    assert get_connecting_coordinates(1, 7, text) == ((1, 6, False), (1, 10, False))
    assert get_connecting_coordinates(1, 8, text) == ((1, 6, False), (1, 10, False))
    assert get_connecting_coordinates(1, 9, text) == ((1, 6, False), (1, 10, False))
    assert get_connecting_coordinates(3, 10, text) == ((3, 8, True), (3, 12, False))
    assert get_connecting_coordinates(4, 5, text) == ((3, 5, False), (6, 5, True))
    assert get_connecting_coordinates(4, 8, text) == ((3, 8, True), (6, 8, False))


def map_coordinates(mapping, list_of_words, text, line_numbers, character_positions):
    offset = 0
    text_one_line = "".join(text.split("\n"))
    for word in list_of_words:
        # we found the word
        i = text_one_line.index(word)
        # create dictionary entries mapping coordinates to the word
        for j, _ in enumerate(word):
            mapping[(line_numbers[offset + i], character_positions[offset + i + j])] = (
                line_numbers[offset + i],
                character_positions[offset + i],
                word,
            )
        # we discard everything up to the word
        text_one_line = text_one_line[i + len(word) :]
        offset += i + len(word)
    return mapping


def locate_all_words(text):
    # list of line numbers for each character
    line_numbers = []
    for i, line in enumerate(text.split("\n")):
        for character in line:
            line_numbers.append(i)

    # list of character positions for each character
    character_positions = []
    for line in text.split("\n"):
        for i, _ in enumerate(line):
            character_positions.append(i)

    # find words like [origin/foo]
    words_with_slash = re.findall(r"\[.*?\]", text)

    # remove these from the text so that we don't find "[origin" and "foo]" in the next step
    # when we remove these, we replace them by spaces to keep the spacing
    _text = text
    for word in words_with_slash:
        _text = _text.replace(word, len(word) * " ")

    # find everything that is not - | / \ v ^ < >
    normal_words = re.findall(r"[^-|/\\v\^\<\>\s+]+", _text)

    words = {}
    for list_of_words in [words_with_slash, normal_words]:
        words = map_coordinates(
            mapping=words,
            list_of_words=list_of_words,
            text=text,
            line_numbers=line_numbers,
            character_positions=character_positions,
        )

    return words


def test_locate_all_words():
    text = r"""
    a-b---eee
       \   \
     x  c<--[d12]
     |  ^
     v  |
     x oh
      \|
       o
       |
       b"""
    assert locate_all_words(text) == {
        (1, 4): (1, 4, "a"),
        (1, 6): (1, 6, "b"),
        (1, 10): (1, 10, "eee"),
        (1, 11): (1, 10, "eee"),
        (1, 12): (1, 10, "eee"),
        (3, 5): (3, 5, "x"),
        (3, 8): (3, 8, "c"),
        (3, 12): (3, 12, "[d12]"),
        (3, 13): (3, 12, "[d12]"),
        (3, 14): (3, 12, "[d12]"),
        (3, 15): (3, 12, "[d12]"),
        (3, 16): (3, 12, "[d12]"),
        (6, 5): (6, 5, "x"),
        (6, 7): (6, 7, "oh"),
        (6, 8): (6, 7, "oh"),
        (8, 7): (8, 7, "o"),
        (10, 7): (10, 7, "b"),
    }


def graph(text):
    words = locate_all_words(text)

    # clean up text: remove words like [origin/foo]
    _text = text
    for word in re.findall(r"\[.*?\]", text):
        _text = _text.replace(word, len(word) * " ")

    coordinate_tuples = []
    lines = _text.split("\n")
    for line_number, line in enumerate(lines):
        for character_position, _ in enumerate(line):
            if lines[line_number][character_position] in ["-", "/", "\\", "|"]:
                c = get_connecting_coordinates(line_number, character_position, text)
                coordinate_tuples.append(c)

    # we remove duplicate tuples that come from "long" connections
    coordinate_tuples = set(coordinate_tuples)

    graph = defaultdict(list)
    for s, e in coordinate_tuples:
        _s = (s[0], s[1])
        _e = (e[0], e[1])
        # <-->
        if s[2] and e[2]:
            es, se = True, True
        # --->
        if (not s[2]) and e[2]:
            es, se = False, True
        # <---
        if s[2] and (not e[2]):
            es, se = True, False
        # ----
        if (not s[2]) and (not e[2]):
            es, se = True, True
        if se:
            angle = get_angle(_s, _e)
            k, v = words[_s], (words[_e][0], words[_e][1], words[_e][2], angle)
            if v not in graph[k]:
                graph[k].append(v)
        if es:
            angle = get_angle(_e, _s)
            k, v = words[_e], (words[_s][0], words[_s][1], words[_s][2], angle)
            if v not in graph[k]:
                graph[k].append(v)
    return graph


def test_graph():
    text = r"""
    a-b---eee
       \   \
     x  c<--[d12]
     |  ^
     v  |
     x oh
      \|
       o
       |
       b"""
    reference = {
        (3, 8, "c"): [(1, 6, "b", 315)],
        (3, 12, "[d12]"): [(3, 8, "c", 270), (1, 10, "eee", 315)],
        (1, 6, "b"): [(1, 10, "eee", 90), (1, 4, "a", 270), (3, 8, "c", 135)],
        (1, 10, "eee"): [(1, 6, "b", 270), (3, 12, "[d12]", 135)],
        (6, 7, "oh"): [(3, 8, "c", 0), (8, 7, "o", 180)],
        (8, 7, "o"): [(6, 7, "oh", 0), (6, 5, "x", 315), (10, 7, "b", 180)],
        (3, 5, "x"): [(6, 5, "x", 180)],
        (6, 5, "x"): [(8, 7, "o", 135)],
        (1, 4, "a"): [(1, 6, "b", 90)],
        (10, 7, "b"): [(8, 7, "o", 0)],
    }
    result = graph(text)
    for node in result:
        assert set(result[node]) == set(reference[node])

    text = r"""
    a->boo
    ^   |  [origin/foo]---[moo]
    |   v  /
    c<--d-e
        | |
        f-g"""
    reference = {
        (1, 4, "a"): [(1, 7, "boo", 90)],
        (4, 4, "c"): [(1, 4, "a", 0)],
        (4, 8, "d"): [(4, 4, "c", 270), (4, 10, "e", 90), (6, 8, "f", 180)],
        (4, 10, "e"): [
            (2, 11, "[origin/foo]", 45),
            (4, 8, "d", 270),
            (6, 10, "g", 180),
        ],
        (2, 11, "[origin/foo]"): [(4, 10, "e", 225), (2, 26, "[moo]", 90)],
        (2, 26, "[moo]"): [(2, 11, "[origin/foo]", 270)],
        (6, 8, "f"): [(6, 10, "g", 90), (4, 8, "d", 0)],
        (6, 10, "g"): [(6, 8, "f", 270), (4, 10, "e", 0)],
        (1, 7, "boo"): [(4, 8, "d", 180)],
    }
    result = graph(text)
    for node in result:
        assert set(result[node]) == set(reference[node])
