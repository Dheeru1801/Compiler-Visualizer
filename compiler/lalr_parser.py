import ply.lex as lex
import ply.yacc as yacc

# List of token names
tokens = (
    'INT', 'FLOAT', 'CHAR',
    'IF', 'ELSE', 'WHILE', 'RETURN',
    'ID', 'NUMBER',
    'PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE',
    'LPAREN', 'RPAREN',
    'LBRACE', 'RBRACE',
    'SEMICOLON', 'ASSIGN',
    'LT', 'GT', 'LE', 'GE', 'EQ', 'NEQ',
    'COMMA'
)

t_PLUS      = r'\+'
t_MINUS     = r'-'
t_MULTIPLY  = r'\*'
t_DIVIDE    = r'/'
t_LPAREN    = r'\('
t_RPAREN    = r'\)'
t_LBRACE    = r'\{'
t_RBRACE    = r'\}'
t_SEMICOLON = r';'
t_ASSIGN    = r'='
t_LT        = r'<'
t_GT        = r'>'
t_LE        = r'<='
t_GE        = r'>='
t_EQ        = r'=='
t_NEQ       = r'!='
t_COMMA     = r','

def t_IF(t):
    r'if'
    return t

def t_ELSE(t):
    r'else'
    return t

def t_WHILE(t):
    r'while'
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

t_ignore = ' \t\r\n'

def t_error(t):
    raise Exception(f"Illegal character '{t.value[0]}' at position {t.lexpos}")

lexer = lex.lex()

# AST Node
class ASTNode:
    def __init__(self, type, value=None, children=None):
        self.type = type
        self.value = value
        # Flatten any nested lists in children
        self.children = []
        if children:
            for child in children:
                if isinstance(child, list):
                    self.children.extend(child)
                else:
                    self.children.append(child)
    def to_dict(self):
        return {
            'type': self.type,
            'value': self.value,
            'children': [c.to_dict() for c in self.children]
        }

# Parse Tree Node
class ParseTreeNode:
    def __init__(self, rule, children=None, value=None):
        self.rule = rule
        self.value = value
        self.children = children or []
    def to_dict(self):
        return {
            'rule': self.rule,
            'value': self.value,
            'children': [c.to_dict() for c in self.children]
        }

def make_parse_tree_node(rule, children=None, value=None):
    return ParseTreeNode(rule, children, value)

# Global to store the parse tree root
parse_tree_root = None

def p_program(p):
    'program : external_declarations'
    global parse_tree_root
    p.slice[0].parse_tree = make_parse_tree_node('program', [getattr(p.slice[1], 'parse_tree', None)])
    parse_tree_root = p.slice[0].parse_tree
    p[0] = ASTNode('Program', children=p[1])

def p_external_declarations_multi(p):
    'external_declarations : external_declarations external_declaration'
    p[0] = p[1] + [p[2]]
    p.slice[0].parse_tree = make_parse_tree_node('external_declarations', [getattr(p.slice[1], 'parse_tree', None), getattr(p.slice[2], 'parse_tree', None)])

def p_external_declarations_single(p):
    'external_declarations : external_declaration'
    p[0] = [p[1]]
    p.slice[0].parse_tree = make_parse_tree_node('external_declarations', [getattr(p.slice[1], 'parse_tree', None)])

def p_external_declaration_function(p):
    'external_declaration : type ID LPAREN params RPAREN block'
    p[0] = ASTNode('FunctionDef', value={'type': p[1], 'name': p[2]}, children=[p[4], p[6]])
    p.slice[0].parse_tree = make_parse_tree_node('function_def', [None, None, None, getattr(p.slice[4], 'parse_tree', None), None, getattr(p.slice[6], 'parse_tree', None)])

def p_external_declaration_statement(p):
    'external_declaration : statement'
    p[0] = p[1]
    p.slice[0].parse_tree = make_parse_tree_node('external_statement', [getattr(p.slice[1], 'parse_tree', None)])

def p_params_multi(p):
    'params : params COMMA param'
    p[0] = p[1] + [p[3]]
    p.slice[0].parse_tree = make_parse_tree_node('params', [getattr(p.slice[1], 'parse_tree', None), None, getattr(p.slice[3], 'parse_tree', None)])

def p_params_single(p):
    'params : param'
    p[0] = [p[1]]
    p.slice[0].parse_tree = make_parse_tree_node('params', [getattr(p.slice[1], 'parse_tree', None)])

def p_params_empty(p):
    'params : '
    p[0] = []
    p.slice[0].parse_tree = make_parse_tree_node('params', [])

def p_param(p):
    'param : type ID'
    p[0] = ASTNode('Param', value={'type': p[1], 'name': p[2]})
    p.slice[0].parse_tree = make_parse_tree_node('param', [None, None])

def p_block(p):
    'block : LBRACE statements RBRACE'
    p[0] = ASTNode('Block', children=p[2])
    p.slice[0].parse_tree = make_parse_tree_node('block', [None, getattr(p.slice[2], 'parse_tree', None), None])

def p_statements_multi(p):
    'statements : statements statement'
    p[0] = p[1] + [p[2]]
    p.slice[0].parse_tree = make_parse_tree_node('statements', [getattr(p.slice[1], 'parse_tree', None), getattr(p.slice[2], 'parse_tree', None)])

def p_statements_single(p):
    'statements : statement'
    p[0] = [p[1]]
    p.slice[0].parse_tree = make_parse_tree_node('statements', [getattr(p.slice[1], 'parse_tree', None)])

def p_statement_declaration(p):
    '''statement : type ID ASSIGN expr SEMICOLON
                 | type ID SEMICOLON'''
    if len(p) == 6:
        p[0] = ASTNode('Declaration', value=p[1], children=[
            ASTNode('Variable', value=p[2]),
            p[4]
        ])
        p.slice[0].parse_tree = make_parse_tree_node('declaration', [getattr(p.slice[1], 'parse_tree', None), None, None, getattr(p.slice[4], 'parse_tree', None), None])
    else:
        p[0] = ASTNode('Declaration', value=p[1], children=[
            ASTNode('Variable', value=p[2])
        ])
        p.slice[0].parse_tree = make_parse_tree_node('declaration', [getattr(p.slice[1], 'parse_tree', None), None, None])

def p_statement_assignment(p):
    'statement : ID ASSIGN expr SEMICOLON'
    p[0] = ASTNode('Assignment', children=[
        ASTNode('Variable', value=p[1]),
        p[3]
    ])
    p.slice[0].parse_tree = make_parse_tree_node('assignment', [None, None, getattr(p.slice[3], 'parse_tree', None), None])

def p_statement_block(p):
    'statement : block'
    p[0] = p[1]
    p.slice[0].parse_tree = make_parse_tree_node('block_stmt', [getattr(p.slice[1], 'parse_tree', None)])

def p_statement_if(p):
    'statement : IF LPAREN expr RPAREN statement'
    p[0] = ASTNode('If', children=[p[3], p[5]])
    p.slice[0].parse_tree = make_parse_tree_node('if', [None, None, getattr(p.slice[3], 'parse_tree', None), None, getattr(p.slice[5], 'parse_tree', None)])

def p_statement_if_else(p):
    'statement : IF LPAREN expr RPAREN statement ELSE statement'
    p[0] = ASTNode('IfElse', children=[p[3], p[5], p[7]])
    p.slice[0].parse_tree = make_parse_tree_node('ifelse', [None, None, getattr(p.slice[3], 'parse_tree', None), None, getattr(p.slice[5], 'parse_tree', None), None, getattr(p.slice[7], 'parse_tree', None)])

def p_statement_while(p):
    'statement : WHILE LPAREN expr RPAREN statement'
    p[0] = ASTNode('While', children=[p[3], p[5]])
    p.slice[0].parse_tree = make_parse_tree_node('while', [None, None, getattr(p.slice[3], 'parse_tree', None), None, getattr(p.slice[5], 'parse_tree', None)])

def p_statement_return(p):
    'statement : RETURN expr SEMICOLON'
    p[0] = ASTNode('Return', children=[p[2]])
    p.slice[0].parse_tree = make_parse_tree_node('return', [None, getattr(p.slice[2], 'parse_tree', None), None])

def p_statement_expr(p):
    'statement : expr SEMICOLON'
    p[0] = p[1]
    p.slice[0].parse_tree = make_parse_tree_node('expr_stmt', [getattr(p.slice[1], 'parse_tree', None), None])

def p_type(p):
    '''type : INT
            | FLOAT
            | CHAR'''
    p[0] = p[1]
    p.slice[0].parse_tree = make_parse_tree_node('type', [None])

def p_expr_binop(p):
    '''expr : expr PLUS term
            | expr MINUS term'''
    p[0] = ASTNode('BinaryOp', value=p[2], children=[p[1], p[3]])
    p.slice[0].parse_tree = make_parse_tree_node('binop', [getattr(p.slice[1], 'parse_tree', None), None, getattr(p.slice[3], 'parse_tree', None)])

def p_expr_relop(p):
    '''expr : expr LT term
            | expr GT term
            | expr LE term
            | expr GE term
            | expr EQ term
            | expr NEQ term'''
    p[0] = ASTNode('RelOp', value=p[2], children=[p[1], p[3]])
    p.slice[0].parse_tree = make_parse_tree_node('relop', [getattr(p.slice[1], 'parse_tree', None), None, getattr(p.slice[3], 'parse_tree', None)])

def p_expr_term(p):
    'expr : term'
    p[0] = p[1]
    p.slice[0].parse_tree = make_parse_tree_node('expr_term', [getattr(p.slice[1], 'parse_tree', None)])

def p_term_binop(p):
    '''term : term MULTIPLY factor
            | term DIVIDE factor'''
    p[0] = ASTNode('BinaryOp', value=p[2], children=[p[1], p[3]])
    p.slice[0].parse_tree = make_parse_tree_node('binop', [getattr(p.slice[1], 'parse_tree', None), None, getattr(p.slice[3], 'parse_tree', None)])

def p_term_factor(p):
    'term : factor'
    p[0] = p[1]
    p.slice[0].parse_tree = make_parse_tree_node('term_factor', [getattr(p.slice[1], 'parse_tree', None)])

def p_factor_number(p):
    'factor : NUMBER'
    p[0] = ASTNode('Number', value=p[1])
    p.slice[0].parse_tree = make_parse_tree_node('number', [], p[1])

def p_factor_id(p):
    'factor : ID'
    p[0] = ASTNode('Variable', value=p[1])
    p.slice[0].parse_tree = make_parse_tree_node('id', [], p[1])

def p_factor_call(p):
    'factor : ID LPAREN args RPAREN'
    p[0] = ASTNode('Call', value=p[1], children=p[3])
    p.slice[0].parse_tree = make_parse_tree_node('call', [None, None, getattr(p.slice[3], 'parse_tree', None), None])

def p_args_multi(p):
    'args : args COMMA expr'
    p[0] = p[1] + [p[3]]
    p.slice[0].parse_tree = make_parse_tree_node('args', [getattr(p.slice[1], 'parse_tree', None), None, getattr(p.slice[3], 'parse_tree', None)])

def p_args_single(p):
    'args : expr'
    p[0] = [p[1]]
    p.slice[0].parse_tree = make_parse_tree_node('args', [getattr(p.slice[1], 'parse_tree', None)])

def p_args_empty(p):
    'args : '
    p[0] = []
    p.slice[0].parse_tree = make_parse_tree_node('args', [])

def p_factor_paren(p):
    'factor : LPAREN expr RPAREN'
    p[0] = p[2]
    p.slice[0].parse_tree = make_parse_tree_node('paren', [None, getattr(p.slice[2], 'parse_tree', None), None])

def p_error(p):
    if p:
        raise Exception(f"Syntax error at '{p.value}'")
    else:
        raise Exception("Syntax error at EOF")

parser = yacc.yacc()

def parse_with_tree(code):
    global parse_tree_root
    parse_tree_root = None
    ast = parser.parse(code)
    # Fix: wrap in Program node if ast is a list
    if isinstance(ast, list):
        ast = ASTNode('Program', children=ast)
    return ast, parse_tree_root 