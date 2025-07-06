from rich.progress import track
from rich import print
from time import sleep
from pygments import lexers
from rich.syntax import Syntax
from rich.console import *
from pygments.lexer import RegexLexer
from pygments.token import Text, Name, Keyword, Punctuation, Number
from prompt_toolkit import PromptSession
from prompt_toolkit.lexers import PygmentsLexer
import os
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style

console = Console()

class TLISPLexer(RegexLexer):
    name = 'TLISP'
    aliases = ['tlisp']
    filenames = ['*.lsp']

    tokens = {
        'root': [
            (r'\s+', Text),
            (r'\(', Punctuation),
            (r'\)', Punctuation),
            (r'\b(def|if|lambda|quote|begin|t|nil|dict|list|princ|py|with)\b', Keyword),
            (r'[a-zA-Z_+\-*/<>=!?:$%&|~^]+', Name),
            (r'\d+', Number)
        ]
    }

def process_data():
    sleep(0.05)

tlisp_completer = WordCompleter([
    'def', 'lambda', 'quote', 'begin',
    'list', 'dict', 'cons', 'cdr', 'car',
    'remove', 'append', 'getk',
    'princ', 'nth', 'py', 't', 'nil',
    'if'], ignore_case=True)

style = Style.from_dict({
    'completion-menu.completion': 'bg:#008888 #ffffff',
    'completion-menu.completion.current': 'bg:#00aaaa #000000',
    'scrollbar.background': 'bg:#88aaaa',
    'scrollbar.button': 'bg:#222222',
})

lexers.LEXERS['TLISP'] = (
    'evaluate.py',
    'TLISPLexer',
    'TLISP',
    ('tlisp',),
    ('*.lsp',)
)

session = PromptSession(
    '> ', lexer=PygmentsLexer(TLISPLexer),
    completer=tlisp_completer, style=style
)

for _ in track(range(100), description='[yellow]Starting... Please wait!'):
    process_data()

os.system('cls')

class Env:
    def __init__(self):
        self.env = {}

    def add(self, name, value):
        self.env[name] = value

    def get(self, name):
        return self.env[name] if name in self.env else 0

    def delete(self, name):
        if name in self.env:
            del self.env[name]

class Proc:
    def __init__(self, lambda_, args):
        self.args, self.lambda_ = args, lambda_

    def __repr__(self):
        return f'<lambda {self.args}>'

old_eval = eval

def rem(lst, el):
    new_lst = lst
    new_lst.remove(el)
    return new_lst

genv = Env()
genv.env = {
    'princ': Proc(lambda *x: print(*x), 'builtins'),
    'list': Proc(lambda *x: [*x], 'builtins'),
    'nth': Proc(lambda lst, ind: lst[ind], ['lst', 'ind']),
    '+': Proc(lambda first, sec: first + sec, ['first', 'sec']),
    '-': Proc(lambda first, sec: first - sec, ['first', 'sec']),
    '*': Proc(lambda first, sec: first * sec, ['first', 'sec']),
    '/': Proc(lambda first, sec: first / sec, ['first', 'sec']),
    '>': Proc(lambda first, sec: first > sec, ['first', 'sec']),
    '<': Proc(lambda first, sec: first < sec, ['first', 'sec']),
    '=': Proc(lambda first, sec: first == sec, ['first', 'sec']),
    '/=': Proc(lambda first, sec: first != sec, ['first', 'sec']),
    'py': Proc(lambda exp: old_eval(exp, globals() | genv.env), ['exp']),
    'getk': Proc(lambda dct, name: dct[name], ['dct', 'name']),
    'append': Proc(lambda lst, el: lst + [el], ['lst', 'el']),
    'remove': Proc(lambda lst, el: rem(lst, el), ['lst', 'el']),
    'car': Proc(lambda lst: lst[0], ['lst']),
    'cdr': Proc(lambda lst: rem(lst, lst[0]), ['lst']),
    'cons': Proc(lambda el, lst: [el] + lst, ['el', 'lst'])
}
 
def lexer(s):
    return s.replace('(',' ( ').replace(')',' ) ').replace('\n', '').split()
 
def parse(tokens):
    if len(tokens) == 0:
        raise SyntaxError('unexpected EOF while reading')
    token = tokens.pop(0)
    if token == '(':
        l = []
        while tokens[0] != ')':
            l.append(parse(tokens))
        tokens.pop(0)
        return l
    elif token == ')':
        raise SyntaxError('unexpected )')
    else:
        return atom(token)
 
def atom(token):
    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            return token

def eval(ast):
    try:
        name = ast[0]
        if type(name) == int or type(name) == float:
            return name
    except:
        return ast
    if name == 'if':
        return eval(ast[2] if eval(ast[1]) else eval(ast[3]))
    elif name == 'with':
        name = ast[1] + '.lsp'
        with open(name, 'r', -1, 'utf-8') as f:
            run_lisp_interpreter(f.read())
    elif name == 'def':
        name = ast[1]
        val = eval(ast[2])
        genv.add(name, val)
    elif name == 'lambda':
        args = ast[1]
        if type(args) != list:
            args = [args]
        return Proc(lambda *args: eval(ast[2]), args)
    elif name == 'quote':
        res = ''
        for i in ast[1:]:
            res += to_lisp(i) + ' '
        return res[0:-1]
    elif name == 'begin':
        res = 'NIL'
        for i in ast[1:]:
            res = eval(i)
        return res
    elif name == 'dict':
        res = {}
        for i in ast[1:]:
            name = i[0]
            val = eval(i[1])
            res[name] = val
        return res
    elif name == 'nil':
        return False
    elif name == 't':
        return True
    else:
        fn = genv.get(name)
        if type(fn) != Proc:
            return fn
        args = [eval(i) for i in ast[1:]]
        if fn.args == 'builtins':
            return fn.lambda_(*args)
        cur = 0
        for i in fn.args:
            eval(parse(lexer(f'(def {i} {args[cur]})')))
            cur += 1
        return fn.lambda_(*args)

def to_lisp(val):
    if isinstance(val, list):
        cur = 0
        for i in val:
            val[cur] = to_lisp(i)
            cur += 1
        return '(' + ' '.join(val) + ')'
    elif isinstance(val, bool) or val == None:
        if val == True:
            return 'T'
        return 'NIL'
    elif isinstance(val, dict):
        cur = 0
        res = '('
        for i in val.values():
            val[list(val.keys())[cur]] = to_lisp(i)
            res += list(val.keys())[cur] + ':' + to_lisp(i) + ' '
            cur += 1
        res = res[0:-1]
        return res + ')'
    return str(val)

def run_lisp_interpreter(code):
    for i in code.split('\n'):
        if i == '' or i.isspace():
            continue
        print(to_lisp(eval(parse(lexer(i)))))
    genv.env = {
        'princ': Proc(lambda *x: print(*x), 'builtins'),
        'list': Proc(lambda *x: [*x], 'builtins'),
        'nth': Proc(lambda lst, ind: lst[ind], ['lst', 'ind']),
        '+': Proc(lambda first, sec: first + sec, ['first', 'sec']),
        '-': Proc(lambda first, sec: first - sec, ['first', 'sec']),
        '*': Proc(lambda first, sec: first * sec, ['first', 'sec']),
        '/': Proc(lambda first, sec: first / sec, ['first', 'sec']),
        '>': Proc(lambda first, sec: first > sec, ['first', 'sec']),
        '<': Proc(lambda first, sec: first < sec, ['first', 'sec']),
        '=': Proc(lambda first, sec: first == sec, ['first', 'sec']),
        '/=': Proc(lambda first, sec: first != sec, ['first', 'sec']),
        'py': Proc(lambda exp: old_eval(exp, globals() | genv.env), ['exp']),
        'getk': Proc(lambda dct, name: dct[name], ['dct', 'name']),
        'append': Proc(lambda lst, el: lst + [el], ['lst', 'el']),
        'remove': Proc(lambda lst, el: rem(lst, el), ['lst', 'el']),
        'car': Proc(lambda lst: lst[0], ['lst']),
        'cdr': Proc(lambda lst: rem(lst, lst[0]), ['lst']),
        'cons': Proc(lambda el, lst: [el] + lst, ['el', 'lst'])
    }

def repl():
      print('[red]TLISP 1.0')
      while True:
          try:
              prompt = session.prompt()
              if prompt == 'exit':
                  return 0
              print('[red]' + to_lisp(eval(parse(lexer(prompt)))))
          except Exception as err:
              print('Error!', err)

if __name__ == '__main__':
    repl()
