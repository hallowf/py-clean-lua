import ply.lex as lex
import ply.yacc as yacc


class PEBCAK(Exception):
    """Regex exceptions"""

    def __init__(self, message, errors=None):
        super().__init__(message, errors)
        self.message = message
        self.errors = errors

    def __str__(self):
        return "{} ({})".format(self.message, self.errors)


tokens = (
    'FUNCTION',
    'COMMENTBLOCK',
    'COMMENT',
    'NAME',
    'LBRCKT',
    'RBRCKT',
    'EQUALS',
    'NUMBER',
    'OP',
    'END',
    'COMMA',
    'LPAREN',
    'RPAREN',
    'STR',
    'IF',
    'MULTISTR',
    'CONCATSTR'
)

reserved = {key: key.upper()
            for key in ['if', 'function', 'end', 'while', 'do', 'for', 'nil', 'then']}


t_COMMENT = r'\s*(--)+\s.*\s'
t_COMMENTBLOCK = r'--*\[\[.*?\]\]'
t_RBRCKT = r'\{'
t_LBRCKT = r'\}'
t_RPAREN = r'\('
t_LPAREN = r'\)'
t_EQUALS = r'='
t_OP = r'[+\-/*]|>=?|<=?|=='
t_COMMA = r','
t_NUMBER = r'[0-9]+'
t_STR = r'\'(.*)*\'|\"(.*)*\"'
t_MULTISTR = r'\['
t_CONCATSTR = r'\.\.'


def t_NAME(t):
    r'[_a-zA-Z][_0-9a-zA-Z]*'
    try:
        t.type = reserved[t.value]
    except KeyError:
        pass
    return t
# Rule for booleans


def t_boolean(t):
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

# Define a rule so we can track line numbers


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    pass


# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)
    exit(1)


# Build the lexer
lexer = lex.lex()

# Statements


def p_program(p):
    '''program : statement
               | statement program'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = [p[1], p[2]]
    # print(len(p))
    # print([*p])


def p_statement(p):
    '''statement : assign
                 | funcdecl
                 | funccall
                 | expression'''
    p[0] = p[1]


def p_assign(p):
    '''assign : NAME EQUALS expression'''
    p[0] = ['ass', p[1], p[3]]


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
            | NAME COMMA args'''
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


def p_funccall(p):
    '''funccall : NAME RPAREN args LPAREN'''
    p[0] = ['funccall', p[1], *p[3]]


# Expressions


def p_expression(p):
    '''expression : NAME
                  | NUMBER
                  | binop'''
    p[0] = p[1]


def p_binop(p):
    '''binop : expression OP expression'''
    if len(p) == 4:
        p[0] = ['comp', p[1], p[2], p[3]]
    else:
        p[0] = ['comp', p[1], p[2], p[3], p[4], p[5]]
    # print("binop", [*p])
    # print("binop len", len(p))


# def p_multbinop(p):
#     '''multbinop : binop
#                  | binop OP expression
#                  | binop OP multbinop'''
#     if len(p) > 2:
#         if len(p[3]) == 1:
#             print("mult 1")
#             p[0] = [*p[1], p[2], p[3]]
#         else:
#             print("mult 2")
#             p[0] = ['multcomp', [p[1], p[2], p[3]]]
#     else:
#         print("mult 3")
#         p[0] = p[1]
#     print("multbinop", [*p])
#     print(len(p))


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
            print(tok)
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
        if type == 'func':
            return "function {}({}){} end".format(node[1], ",".join(node[2]), " ".join([uglify_node(statement) for statement in node[3]]))
        elif type == 'funccall':
            return "{}({})".format(node[1], ",".join(node[2]))
        elif type == "ass":
            if len(node[2]) == 1:
                return "{}={}".format(node[1], node[2])
            else:
                return "{}={}".format(node[1], " ".join([uglify_node(assi) for assi in node[2]]))
        elif type == 'comp':
            # print([*node])
            # print(len(node))
            return "{}{}{}".format(node[1], node[2], node[3])
        else:
            assert False
    return uglify_node(ast)


def lython(ast):

    def lython_node(node):
        type = node[0]
        if type == 'func':
            return "def {}({})\n\t{}".format(node[1], ",".join(node[2]), " ".join([lython_node(statement) for statement in node[3]]))
        elif type == "ass":
            return "{}={}".format(node[1], node[2])
        elif type == 'comp':
            return "{}{}{}".format(node[1], node[2], node[3])
        else:
            assert False
    return lython_node(ast)


def write_to_file(code, file):
    with FileHandler(file, "w") as w:
        w.write(code)


with open("test.lua", "r") as c:
    text = c.read()
    # print_tokens(text)
    ast = parser.parse(text)
    print("ast", ast)
    if isinstance(ast[0], str):
        print(uglify(ast))
    else:
        print([uglify(statem) for statem in ast])
    # print("Done")
