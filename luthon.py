import ply.lex as lex
import ply.yacc as yacc
from devutils import Printer

printer = Printer()
prnt = printer.prnt


class PEBCAK(Exception):
    """Regex exceptions"""

    def __init__(self, message, errors=None):
        super().__init__(message, errors)
        self.message = message
        self.errors = errors

    def __str__(self):
        return "{} ({})".format(self.message, self.errors)


tokens = (
    'COMMENTBLOCK',
    'COMMENT',
    'NAME',
    'LBRCKT',
    'RBRCKT',
    'EQUALS',
    'NUMBER',
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE',
    'LESS',
    'GREATER',
    'LESSEQUALS',
    'GREATEREQUALS',
    'ISEQUAL',
    'UMINUS',
    'COMMA',
    'LPAREN',
    'RPAREN',
    'STR',
    'MULTISTR',
    'CONCATSTR',
    'FLOAT'
)

reserved = {key: key.upper()
            for key in ['if', 'else', 'elseif', 'function', 'end', 'while', 'do', 'for', 'nil', 'then', 'and', 'or', 'true', 'false', 'in']}

# IMPORTANT: add reserved keywords to tokens
for tup in reserved.items():
    tokens += tup


t_RBRCKT = r'\{'
t_LBRCKT = r'\}'
t_RPAREN = r'\('
t_LPAREN = r'\)'
t_EQUALS = r'='
t_PLUS = r'\+'
t_MINUS = r'\-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_LESS = r'<'
t_GREATER = r'>'
t_LESSEQUALS = r'<='
t_GREATEREQUALS = r'>='
t_ISEQUAL = r'=='
# # TODO: check this token is valid
# t_UMINUS = r'\-([0-9]*|[_a-zA-Z][_0-9a-zA-Z]*)'
t_COMMA = r','
t_STR = r'\'(.*)*\'|\"(.*)*\"'
t_MULTISTR = r'\['
t_CONCATSTR = r'\.\.'
t_IPAIRS = r'ipairs'

# https://www.dabeaz.com/ply/ply.html#ply_nn27
precedence = (
    ('left', 'AND'),
    ('left', 'OR'),
    ('left', 'LESS', 'GREATER', 'ISEQUAL'),
    ('left', 'TIMES', 'DIVIDE'),
    ('left', 'PLUS', 'MINUS'),
)


def t_NAME(t):
    r'[_a-zA-Z][_0-9a-zA-Z]*'
    try:
        t.type = reserved[t.value]
    except KeyError:
        pass
    return t
# Rule for booleans


def t_NUMBER(t):
    r'[0-9]+'
    t.value = int(t.value)
    return t


def t_FLOAT(t):
    r'\-?[0-9]+[.][0-9]+'
    t.value = float(t.value)
    print(t)
    return t


def t_BOOLEAN(t):
    r'true|false'
    if (t.value == "true"):
        t.value = True
        # print(t)
    elif (t.value == "false"):
        t.value = False
        # print(t)
    else:
        raise PEBCAK("Not a boolean", t.value)
    return t


def t_whitespace(t):
    r'[ \t]+'
    pass


def t_commentblock(t):
    r'--+\[\[(.*)\]\]'
    # TODO: Failing to ignore blocks that end at new line:
    # --[[ something
    # ]]
    pass


def t_comment(t):
    r'(--)+.*'
    pass


def t_newline(t):  # Define a rule so we can track line numbers
    r'\n+'
    t.lexer.lineno += len(t.value)
    pass


def t_error(t):  # Error handling rule
    print("Illegal character '{}' at line {}".format(
        t.value[0], t.lexer.lineno))
    t.lexer.skip(1)
    exit(1)


# Build the lexer
lexer = lex.lex()

# Statements


def p_program(p):
    '''program : statement
               | statement program'''
    prnt("program", p)
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = ["prog", p[1], [*p[2]]]


def p_statement(p):
    '''statement : assign
                 | funcdecl
                 | expression
                 | condition
                 | whilel
                 | forl'''
    p[0] = p[1]


def p_loop_iters(p):
    '''liters : expression COMMA expression'''
    prnt("liters", p)
    p[0] = [p[1], p[3]]


def p_for_loop(p):
    '''forl : FOR NAME EQUALS liters DO END'''
    prnt("forl", p)
    last = [*p][-1]
    penult = [*p][-2]
    if last == "end" and penult == "do":
        p[0] = ['for', p[2], p[4]]


def p_while_loop(p):
    '''whilel : WHILE expression DO body END'''
    prnt("while", p)
    last = [*p][-1]
    penult = [*p][-2]
    if last == "end" and not penult:
        p[0] = ["whilel", p[2]]
    else:
        p[0] = ["whilel", p[2], [*p[4]]]


def p_isequal(p):
    '''isequal : expression ISEQUAL expression'''
    print("isequal", [*p])
    print("isequal len", len(p))
    p[0] = ['ieq', p[1], p[3]]


def p_elseclauses(p):
    '''elseclauses : ELSEIF expression THEN condstate elseclauses
                   | ELSE condstate'''
    prnt("elseclauses", p)
    if len(p) == 1:
        pass
    elif p[1] == 'elseif':
        p[0] = ["elseif", p[2], p[4], *p[5]]
    else:
        p[0] = ["else", [p[2]]]


def p_condstate(p):
    '''condstate : statement
                 | statement condstate'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        if isinstance(p[2][0], str):
            p[0] = [p[1], p[2]]
        else:
            p[0] = [p[1], *p[2]]


def p_andor(p):
    '''andor : expression AND expression
             | expression OR expression'''
    prnt("andor", p)
    if len(p[3]) == 1:
        p[0] = [p[2].lower(), p[1], p[3]]
    else:
        p[0] = [p[2].lower(), p[1], p[3]]


def p_condition(p):
    '''condition : IF expression THEN END
                 | IF expression THEN condstate END
                 | IF expression THEN condstate elseclauses END'''
    last = [*p][-1]
    penult = [*p][-2]
    prnt("condition", p)
    if penult == "then" and last == 'end':
        if p[3][0] == "and" or p[3][0] == "or":
            p[0] = ["cond", p[2], p[3]]
        else:
            p[0] = ["cond", p[2]]
    elif last == "end" and penult[0] != "else" or penult[0] != "elseif":
        if p[3][0] == "and" or p[3][0] == "or":
            p[0] = ["cond", p[2], p[3], p[4]]
        else:
            p[0] = ["cond", p[2], p[4]]
    else:
        p[0] = ["cond", p[2], p[4], p[5]]


def p_assign(p):
    '''assign : NAME EQUALS expression'''
    print("assign", len(p))
    print("assign", [*p])
    if len(p[3]) == 1:
        p[0] = ['ass', p[1], p[3]]
    else:
        # print(p[3])
        p[0] = ['ass', p[1], [p[3]]]


def p_body(p):
    '''body :
            | statement body'''
    if len(p) == 1:
        p[0] = []
    else:
        p[0] = [p[1], *p[2]]


def p_args(p):
    '''args :
            | NAME
            | NUMBER
            | NAME COMMA args
            | NUMBER COMMA args'''
    if len(p) == 1:
        p[0] = []
    elif len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1], *p[3]]
    # print("args", [*p])


def p_funcdecl(p):
    '''funcdecl : FUNCTION NAME RPAREN args LPAREN body END'''
    p[0] = ['func', p[2], p[4], p[6]]
    # print(len(p))
    # print([*p])


# Expressions


def p_expression(p):
    '''expression : binop
                  | andor
                  | isequal
                  | NUMBER
                  | NAME
                  | funccall
                  | TRUE
                  | FALSE
                  | FLOAT'''
    p[0] = p[1]


def p_funccall(p):
    '''funccall : NAME RPAREN args LPAREN'''
    p[0] = ['funccall', p[1], *p[3]]


def p_binop(p):
    '''binop : expression PLUS expression
             | expression MINUS expression
             | expression TIMES expression
             | expression DIVIDE expression'''
    prnt("binop", p)
    if len(str(p[1])) == 1:
        p[0] = ['bop', p[1], p[2], p[3]]
    else:
        p[0] = ['bop', [*p[1]], p[2], p[3]]


def p_error(p):
    print("Syntax error")
    print(p)
    exit(1)


parser = yacc.yacc()


found = {token: 0 for token in tokens}
keys = [key for key in found.keys()]
to_ignore = {
    'LBRCKT': True, 'RBRCKT': True, 'NAME': False,
    'TABLE': True, 'COMMENTBLOCK': True, 'COMMENT': True,
    'EQUALS': False, 'RPAREN': False, 'LPAREN': False, 'END': True,
    'COMMA': True, 'FUNCTION': True, 'OP': False, 'NUMBER': False


}


def print_tokens(input):
    lexer.input(input)
    while True:
        tok = lexer.token()
        ign = [key for key, val in to_ignore.items() if val == True]
        if not tok:
            print(found)
            break
        tok_type = tok.type
        if tok_type in keys:
            found[tok_type] = found[tok_type] + 1
        if tok_type in ign:
            continue
        else:
            print("tok", tok)
            continue


class FileHandler():
    def __init__(self, file, mode):
        self.name = file
        self.mode = mode

    def __enter__(self):
        self.file = open(self.name, self.mode)
        return self.file

    def __exit__(self, type, value, traceback):
        if value:
            traceback.print_exc(file=sys.stdout)
        self.file.close()


def uglify(ast):

    def uglify_node(node):
        type = node[0]
        # print([*node])
        if type == 'prog':
            print("prog", [*node])
            print("prog len", len(node))
            prog = uglify_node(node[1]) if len(node) == 2 else "{} {}".format(
                uglify_node(node[1]), uglify_node(node[2]))
            return prog
        elif type == 'func':
            return "function {}({}){} end".format(node[1], ",".join(node[2]), " ".join([uglify_node(statement) for statement in node[3]]))
        elif type == 'whilel':
            prnt("whilel", node)
            a_node = node[1] if isinstance(
                node[1], str) else uglify_node(node[1])
            if len(node) == 2:
                return "while {} do end".format(a_node)
            else:
                b_node = node[2] if isinstance(
                    node[2], str) else " ".join(uglify_node(body) for body in node[2])
                return "while {} do {} end".format(a_node, b_node)
        elif type == 'for':
            prnt("for", node)
            a_node = ",".join(str(iterv) for iterv in node[2]) if isinstance(
                node[2], list) else node[2]
            if len(node) == 3:
                return "for {} ={} do end".format(node[1], a_node)
        elif type == 'and' or type == 'or' or type == "ieq":
            prnt("andorieq", node)
            op = type if type == "and" or type == "or" else "=="
            a_node = node[1] if len(node[1]) == 1 else uglify_node(node[1])
            b_node = node[2] if len(node[2]) == 1 else uglify_node(node[2])
            return "{} {} {}".format(a_node, op, b_node)
        elif type == 'funccall':
            print("funccall", [*node])
            if len(node) > 2:
                if len(node[2]) == 1:
                    return "{}({})".format(node[1], node[2])
                else:
                    return "{}({})".format(node[1], ",".join(node[2]))
            else:
                return node[1] + "()"
        elif type == "ass":
            print("ass", node)
            print("ass", len(node[2]))
            if len(*node[2]) == 1:
                print(node[1], node[2])
                return "{}={}".format(node[1], node[2])
            else:
                return "{}={}".format(node[1], " ".join([uglify_node(assi) for assi in node[2]]))
        elif type == 'cond':
            print("cond", [*node])
            print("condlen", len(node))
            if len(node) == 2:
                a_node = node[1] if isinstance(
                    node[1], str) else uglify_node(node[1])
                return "if {} then end".format(a_node)
            elif node[-2] != "then" and node[-1] != "end":
                if isinstance(node[2][0], str):
                    return "if {} {} then {} end".format(node[1], uglify_node(node[2]))
                else:
                    return "if {} {} then {} end".format(node[1], " ".join([uglify_node(statem) for statem in node[2]]))
            else:
                if node[3][0] == "else":
                    if isinstance(node[2][0], str):
                        return "if {} then {} else {} end".format(node[1], uglify_node(node[2]), " ".join([uglify_node(statem) for statem in node[3][1]]))
                    else:
                        return "if {} then {} else {} end".format(node[1], " ".join([uglify_node(statem) for statem in node[2]]), " ".join([uglify_node(statem) for statem in node[3][1]]))
        elif type == 'bop':
            prnt("bop", node)
            a_node = uglify_node(node[1]) if isinstance(
                node[1], list) else node[1]
            return "{}{}{}".format(a_node, node[2], node[3])
        else:
            raise PEBCAK("Invalid type", type)
    return uglify_node(ast)


def luthon(ast):

    def luthon_node(node):
        type = node[0]
        if type == 'func':
            return "def {}({}):\n\t{}".format(node[1], ",".join(node[2]), " ".join([luthon_node(statement) for statement in node[3]]))
        elif type == "ass":
            if len(*node[2]) == 1:
                return "{}={}".format(node[1], node[2])
            else:
                return "{}={}".format(node[1], " ".join([luthon_node(assi) for assi in node[2]]))
        elif type == 'comp':
            if isinstance(node[3], str):
                return "{}{}{}".format(node[1], node[2], node[3])
            else:
                return "{}{}{}".format(node[1], node[2], "".join([luthon_node(comp) for comp in node[3]]))
        else:
            raise PEBCAK("Invalid type " + str(type), node)
    return luthon_node(ast)


def write_to_file(code, file):
    with FileHandler(file, "w") as w:
        w.write(code)


with open("test.lua", "r") as c:
    text = c.read()
    # print_tokens(text)
    ast = parser.parse(text)
    if isinstance(ast[0], str):
        print(uglify(ast))
    else:
        print([uglify(statem) for statem in ast])
        print(" ".join([uglify(node) for node in ast]))
    print("Done")
