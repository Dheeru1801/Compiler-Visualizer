import re
import ply.lex as lex

class Token:
    def __init__(self, type, value, line, column):
        self.type = type
        self.value = value
        self.line = line
        self.column = column
    
    def to_dict(self):
        return {
            'type': self.type,
            'value': self.value,
            'line': self.line,
            'column': self.column
        }

# Token definitions
tokens = (
    'INT', 'FLOAT', 'CHAR',
    'IF', 'ELSE', 'WHILE', 'FOR', 'RETURN',
    'ID', 'NUMBER', 'STRING',
    'PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE',
    'LPAREN', 'RPAREN',
    'LBRACE', 'RBRACE',
    'LBRACKET', 'RBRACKET',
    'SEMICOLON', 'ASSIGN',
    'LT', 'GT', 'LE', 'GE', 'EQ', 'NEQ',
    'COMMA', 'INCREMENT', 'DECREMENT'
)

# Regular expression rules for tokens
t_PLUS      = r'\+'
t_MINUS     = r'-'
t_MULTIPLY  = r'\*'
t_DIVIDE    = r'/'
t_LPAREN    = r'\('
t_RPAREN    = r'\)'
t_LBRACE    = r'\{'
t_RBRACE    = r'\}'
t_LBRACKET  = r'\['
t_RBRACKET  = r'\]'
t_SEMICOLON = r';'
t_ASSIGN    = r'='
t_LT        = r'<'
t_GT        = r'>'
t_LE        = r'<='
t_GE        = r'>='
t_EQ        = r'=='
t_NEQ       = r'!='
t_COMMA     = r','
t_INCREMENT = r'\+\+'
t_DECREMENT = r'--'

# Ignore whitespace
t_ignore = ' \t\r\n'

def t_COMMENT_SINGLE(t):
    r'//.*'
    pass  # No return value. Token discarded

def t_COMMENT_MULTI(t):
    r'/\*(.|\n)*?\*/'
    t.lexer.lineno += t.value.count('\n')  # Update line number
    pass  # No return value. Token discarded

def t_IF(t):
    r'if'
    return t

def t_ELSE(t):
    r'else'
    return t

def t_WHILE(t):
    r'while'
    return t

def t_FOR(t):
    r'for'
    return t

def t_RETURN(t):
    r'return'
    return t

def t_INT(t):
    r'int'
    return t

def t_FLOAT(t):
    r'float'
    return t

def t_CHAR(t):
    r'char'
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_STRING(t):
    r'"[^"]*"'
    t.value = t.value[1:-1]  # Remove the quotes
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    t.lexer.column = 1

def t_error(t):
    raise Exception(f"Illegal character '{t.value[0]}' at position {t.lexpos}")

# Create lexer
lexer = lex.lex()

class Lexer:
    def __init__(self, text):
        self.text = text
        self.lexer = lex.lex()
        self.lexer.input(text)
        self.lexer.lineno = 1
        self.lexer.column = 1
    
    def tokenize(self):
        tokens = []
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            token = Token(tok.type, tok.value, tok.lineno, tok.lexpos - self.lexer.lexdata.rfind('\n', 0, tok.lexpos))
            tokens.append(token)
        return tokens