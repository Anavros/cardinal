
import re
import os
import shlex


"""Malt
A tiny toolkit for structured input and output.
"""

PREFIX = '[malt] '
PROMPT = '> '
COMMENT = '#'
SYNTAX = '?'
INCLUDED_FUNCTIONS = [
    'help',
    'clear',
    'quit',
]

### PUBLIC FUNCTIONS ###


def offer(options):
    """Offer the user a list of options. Input is verified as returned as a
    Response object."""

    if not options or type(options) is not list:
        raise ValueError("Must offer a list of options!")

    try:
        cmd, args = _parse(input(PROMPT), options+INCLUDED_FUNCTIONS)
    except ValueError as e:
        print(e)
        return Response(None)
    except (KeyboardInterrupt, EOFError):
        print()
        raise SystemExit # doesn't print stack trace

    if cmd in _firsts(INCLUDED_FUNCTIONS):
        # divert to included convenience functions
        _redirect(Response(cmd, args), options)
        return Response(None)
    else:
        return Response(cmd, args)


def harvest(filepath, options=None):
    """Load a config file matching syntax against given options."""

    lines = []
    if not options: # must be in lang file
        options = _harvest_syntax(filepath)
        if not options: # still
            raise Exception("Language syntax not provided or found in file.")

    with open(filepath, 'r') as f:
        for raw_line in f:
            # clear out any comments or empty lines
            line = raw_line.split(COMMENT)[0].strip()
            if not line:
                continue

            if line[0] == SYNTAX:
                continue

            # start doing things?
            (cmd, args) = _parse(line, options)
            lines.append((cmd, args))
    return lines


def _harvest_syntax(filepath):
    syntax = []
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            if line[0] == SYNTAX:
                line = line.strip(SYNTAX).strip()
                syntax.append(line)
    return syntax


def serve(content='', end='\n', indent=0):
    def more():
        return min(indent+4, 40)
    def less():
        return max(indent-4, 0)
    if type(content) in [str, int, float]:
        print(content)
    elif type(content) in [list, set, frozenset, tuple]:
        indent = more()
        print('[')
        for i, item in enumerate(content):
            print(' '*indent, end='')
            print("[{}] ".format(i), end='')
            serve(item, indent=indent)
        indent = less()
        print(' '*indent, end='')
        print(']')
    elif type(content) is dict:
        print('{')
        indent = more()
        for (key, value) in content.items():
            print(' '*indent, end='')
            print("{}: ".format(key), end='')
            serve(value)
        indent = less()
        print(' '*indent, end='')
        print('}')
    # Helps with OrderedDict.
    elif hasattr(content, 'items'):
        serve(list(content.items()))
    # Stops objects like str from spewing everywhere.
    elif hasattr(content, '__dict__') and type(content.__dict__) is dict:
        serve(content.__dict__, end)
    elif hasattr(content, '_get_args()'):
        serve(list(content._get_args()))
    # When in doubt, use repr.
    else:
        print(repr(content), end=end)


### INTERNAL FUNCTIONS ###


def _redirect(response, options=[]):
    if response == 'help':
        _help(options)
    elif response == 'clear':
        _clear()
    elif response == 'quit':
        _quit()
    else:
        raise Exception("I've made a terrible mistake.")


def _help(options):
    indent = 0
    def more():
        return min(indent+4, 40)
    def less():
        return max(indent-4, 0)
    print(PREFIX + "Available Options:")
    indent = more()
    for i, opt_line in enumerate(options):
        (cmd, keys, casts) = _opt_parse(opt_line)
        print(' '*indent, end='')
        print('[{}] {}'.format(i, cmd))
        indent = more()
        for key, cast in zip(keys, casts):
            print(' '*indent, end='')
            print("- {}: {}".format(key, cast))
        indent = less()
    indent = less()


def _quit():
    raise SystemExit


def _clear():
    os.system("cls" if os.name == "nt" else "clear")


class Response(object):
    def __init__(self, cmd=None, args=None):
        self.cmd = cmd
        if args is not None:
            for k, v in args.items():
                self.__dict__[k] = v
    def __eq__(self, string):
        return self.cmd == string


def _parse(arg_line, options):
    opt_line = _match_option(arg_line, options) # raises ValueError
    (cmd, values) = _arg_parse(arg_line)
    (_, keys, casts) = _opt_parse(opt_line)
    if not (len(values) == len(keys) == len(casts)):
        raise ValueError("Too many or too few arguments.")
    args = {}
    for key, value, cast in zip(keys, values, casts):
        if '(' in cast: # used for limited options: "arg:str(one|two|three)"
            halves = cast.split('(')
            cast = halves[0]
            allowed_values = halves[1].strip(')').split('|')
            args[key] = _typecast(value, cast, allowed_values)
        else:
            args[key] = _typecast(value, cast)
    return (cmd, args)


def _match_option(arg_line, options):
    for opt_line in options:
        arg_words = shlex.split(arg_line)
        opt_words = shlex.split(opt_line)
        # check command and length of argument list
        if (arg_words[0] == opt_words[0]) and (len(arg_words) == len(opt_words)):
            return opt_line
    # if not found
    raise ValueError("unknown command: {}".format(arg_words[0]))


def _opt_parse(opt_line):
    opt_words = shlex.split(opt_line)
    cmd = opt_words.pop(0) # removes command from front
    names = []
    casts = []
    for opt in opt_words:
        halves = opt.split(':')
        # arg:type becomes arg, type
        if len(halves) == 2:
            name = halves[0]
            cast = halves[1]
        # default to str if no type is given
        elif len(halves) == 1:
            name = halves[0]
            cast = 'str'
        else:
            raise ValueError("malformed expression")
        names.append(name)
        casts.append(cast)
    return (cmd, names, casts)


def _arg_parse(arg_line):
    arg_words = shlex.split(arg_line)
    # KeyError on len() == 1? XXX
    return (arg_words[0], arg_words[1:])


def _typecast(value, cast, allowed_values=None):
    if allowed_values and value not in allowed_values:
        raise ValueError("{} is not an allowed value.".format(value))
        if cast == "str":
            value = str(value)
        elif cast == "int":
            value = int(value)
        elif cast == "float":
            value = float(value)
        else:
            raise ValueError("Unknown cast: {}.".format(cast))
    return value


def _firsts(list_of_strings):
    return [shlex.split(string)[0] for string in list_of_strings]
