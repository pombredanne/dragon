import sys
import os, os.path
from io import open
import glob, time

from lark import Lark
from lark.indenter import Indenter

from haxe_transformer import HaxeTransformer

__path__ = os.path.dirname(__file__)

###########
# TODO: turn this into an abstraction that doesn't rely on Lark directly
# TODO: create a flat list of nodes. This can be a dictionary of names and
# values, for example. This helps us write unit-tests and be parser-agnostic.
# Ultimately, that's what the parser should do: return node (including the
# original line) in a linear order so we can transform it.

# TODO: Lark gives us line-numbers. Write a second grammar on top
# of the Python one (eg. for @:...), run it as a second pass, and
# inject your changes in the right place in the source. Maybe.
##########
class PythonIndenter(Indenter):
    NL_type = '_NEWLINE'
    OPEN_PAREN_types = ['__LPAR', '__LSQB', '__LBRACE']
    CLOSE_PAREN_types = ['__RPAR', '__RSQB', '__RBRACE']
    INDENT_type = '_INDENT'
    DEDENT_type = '_DEDENT'
    tab_len = 4

grammar2_filename = os.path.join(__path__, 'python2.g')
grammar3_filename = os.path.join(__path__, 'python3.g')
with open(grammar2_filename) as f:
    python_parser2 = Lark(f, parser='lalr', postlex=PythonIndenter(), start='file_input')
with open(grammar3_filename) as f:
    python_parser3 = Lark(f, parser='lalr', postlex=PythonIndenter(), start='file_input')


with open(grammar2_filename) as f:
    python_parser2_earley = Lark(f, parser='lalr', lexer='standard', postlex=PythonIndenter(), start='file_input')

def _read(fn, *args):
    kwargs = {'encoding': 'iso-8859-1'}
    with open(fn, *args, **kwargs) as f:
        return f.read()

def _get_lib_path():
    if os.name == 'nt':
        if 'PyPy' in sys.version:
            return os.path.join(sys.prefix, 'lib-python', sys.winver)
        else:
            return os.path.join(sys.prefix, 'Lib')
    else:
        return [x for x in sys.path if x.endswith('%s.%s' % sys.version_info[:2])][0]

def test_python_lib():

    path = _get_lib_path()

    start = time.time()
    files = glob.glob(path+'/*.py')
    for f in files:
        print( f )
        try:
            # print list(python_parser.lex(_read(os.path.join(path, f)) + '\n'))
            try:
                xrange
            except NameError:
                python_parser3.parse(_read(os.path.join(path, f)) + '\n')
            else:
                python_parser2.parse(_read(os.path.join(path, f)) + '\n')
        except:
            print ('At %s' % f)
            raise

    end = time.time()
    print( "test_python_lib (%d files), time: %s secs"%(len(files), end-start) )

def test_earley_equals_lalr():
    path = _get_lib_path()

    files = glob.glob(path+'/*.py')
    for f in files:
        print( f )
        tree1 = python_parser2.parse(_read(os.path.join(path, f)) + '\n')
        tree2 = python_parser2_earley.parse(_read(os.path.join(path, f)) + '\n')
        assert tree1 == tree2

def test_template():

    path = os.path.join("..", "..", "template", "source")
    print("Parsing files at {}".format(path))

    start = time.time()
    files = glob.glob(path+'/main.py')
    for f in files:
        print("Parsing {}".format(f))
        try:
            full_path = os.path.join(path, f)
            # print list(python_parser.lex(_read(os.path.join(path, f)) + '\n'))
            try:
                xrange
            except NameError:
                tree = python_parser3.parse(_read(full_path) + '\n')
                raw_tree = python_parser3.parse(_read(full_path) + '\n')
            else:
                tree = python_parser2.parse(_read(full_path) + '\n')
                raw_tree = python_parser2.parse(_read(full_path) + '\n')
            
            print("{}".format(raw_tree))
            tree = HaxeTransformer().transform(tree)
            convert_and_print(tree, full_path)              
        except:
            print ('Failure at %s' % f)
            raise

    end = time.time()
    print( "test_python_lib (%d files), time: %s secs"%(len(files), end-start) )

    # Make sure this worked.
    with open(os.path.join("..", "..", "template", "source", "main.hx")) as f:
        text = f.read()

    if not HaxeTransformer.MARKER in text:
        raise ValueError("Marker not found in text")
    elif not "from flixel.flx_game import FlxGame" in text:
        raise ValueError("Import not found in text")
    return tree

def convert_and_print(tree, filename):
    filename = filename.replace('.py', '.hx')
    with open(filename, 'wt') as f:
        f.write(tree.pretty())

if __name__ == '__main__':
    # test_python_lib()
    # test_earley_equals_lalr()
    # python_parser3.parse(_read(sys.argv[1]) + '\n')
    test_template()