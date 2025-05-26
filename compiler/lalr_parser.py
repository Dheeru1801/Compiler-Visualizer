import ply.lex as lex
import ply.yacc as yacc

# -----------------------------
# LEXER SECTION
# -----------------------------
# This section defines the tokens and lexer rules for the C-like language.

# List of token names
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
t_LBRACKET  = r'\['
t_RBRACKET  = r'\]'

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

# New token for string literals
def t_STRING(t):
    r'"([^"\\]*(\\.[^"\\]*)*)"'
    t.value = t.value[1:-1]  # Remove the surrounding quotes
    return t

t_ignore = ' \t\r\n'

def t_COMMENT_SINGLE(t):
    r'//.*'
    pass  # No return value. Token discarded

def t_COMMENT_MULTI(t):
    r'/\*(.|\n)*?\*/'
    t.lexer.lineno += t.value.count('\n')  # Update line number
    pass  # No return value. Token discarded

def t_error(t):
    raise Exception(f"Illegal character '{t.value[0]}' at position {t.lexpos}")

lexer = lex.lex()

# -----------------------------
# AST NODE DEFINITIONS
# -----------------------------
# ASTNode: Represents nodes in the abstract syntax tree (AST).
# ParseTreeNode: Represents nodes in the parse tree for visualization.
# Helper functions for parse tree construction.

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
    """Create a parse tree node with safe handling of children"""
    if children is None:
        children = []
    # Filter out None values from children
    children = [c for c in children if c is not None]
    return ParseTreeNode(rule, children, value)

# Global to store the parse tree root
parse_tree_root = None

def get_parse_tree(slice_obj):
    """Helper function to safely get parse tree from a slice object"""
    if slice_obj is None:
        return None
    return getattr(slice_obj, 'parse_tree', None)

# -----------------------------
# PARSER RULES (GRAMMAR)
# -----------------------------
# The following functions define the grammar rules for the language using PLY's yacc.
# Each function corresponds to a grammar rule and constructs AST and parse tree nodes.

# Program structure
# -----------------
# program: The root of the AST, representing the entire program.
# external_declarations: Handles multiple top-level declarations (functions, global statements).

def p_program(p):
    'program : external_declarations'
    global parse_tree_root
    children = [get_parse_tree(p.slice[1])] if p.slice[1] else []
    p.slice[0].parse_tree = make_parse_tree_node('program', children)
    parse_tree_root = p.slice[0].parse_tree
    p[0] = ASTNode('Program', children=p[1] if isinstance(p[1], list) else [p[1]])

def p_external_declarations_multi(p):
    'external_declarations : external_declarations external_declaration'
    p[0] = p[1] + [p[2]]
    children = [get_parse_tree(p.slice[1]), get_parse_tree(p.slice[2])]
    p.slice[0].parse_tree = make_parse_tree_node('external_declarations', children)

def p_external_declarations_single(p):
    'external_declarations : external_declaration'
    p[0] = [p[1]]
    children = [get_parse_tree(p.slice[1])]
    p.slice[0].parse_tree = make_parse_tree_node('external_declarations', children)

# Function definitions and parameters
# -----------------------------------
# Handles function definitions, parameter lists, and parameter nodes.

def p_external_declaration_function(p):
    '''external_declaration : type ID LPAREN params RPAREN block
                          | type ID LPAREN RPAREN block'''
    if len(p) == 7:  # Function with parameters
        p[0] = ASTNode('FunctionDef', value={'type': p[1], 'name': p[2]}, children=[p[4], p[6]])
        children = [
            make_parse_tree_node('type', [], p[1]),
            make_parse_tree_node('id', [], p[2]),
            make_parse_tree_node('lparen', [], '('),
            get_parse_tree(p.slice[4]),
            make_parse_tree_node('rparen', [], ')'),
            get_parse_tree(p.slice[6])
        ]
    else:  # Function without parameters
        p[0] = ASTNode('FunctionDef', value={'type': p[1], 'name': p[2]}, children=[[], p[5]])
        children = [
            make_parse_tree_node('type', [], p[1]),
            make_parse_tree_node('id', [], p[2]),
            make_parse_tree_node('lparen', [], '('),
            make_parse_tree_node('rparen', [], ')'),
            get_parse_tree(p.slice[5])
        ]
    p.slice[0].parse_tree = make_parse_tree_node('function_def', children)

def p_external_declaration_statement(p):
    'external_declaration : statement'
    p[0] = p[1]
    p.slice[0].parse_tree = make_parse_tree_node('external_statement', [getattr(p.slice[1], 'parse_tree', None)])

def p_params_multi(p):
    'params : params COMMA param'
    p[0] = p[1] + [p[3]]
    children = [
        get_parse_tree(p.slice[1]),
        make_parse_tree_node('comma', [], ','),
        get_parse_tree(p.slice[3])
    ]
    p.slice[0].parse_tree = make_parse_tree_node('params', children)

def p_params_single(p):
    'params : param'
    p[0] = [p[1]]
    children = [get_parse_tree(p.slice[1])]
    p.slice[0].parse_tree = make_parse_tree_node('params', children)

def p_params_empty(p):
    'params : '
    p[0] = []
    p.slice[0].parse_tree = make_parse_tree_node('params', [])

def p_param(p):
    '''param : type ID
             | type ID LBRACKET RBRACKET
             | type ID LBRACKET NUMBER RBRACKET'''
    if len(p) == 3:  # Regular parameter
        p[0] = ASTNode('Param', value={'type': p[1], 'name': p[2]})
        children = [
            make_parse_tree_node('type', [], p[1]),
            make_parse_tree_node('id', [], p[2])
        ]
    elif len(p) == 5:  # Array parameter without size
        p[0] = ASTNode('Param', value={'type': p[1], 'name': p[2], 'is_array': True})
        children = [
            make_parse_tree_node('type', [], p[1]),
            make_parse_tree_node('id', [], p[2]),
            make_parse_tree_node('lbracket', [], '['),
            make_parse_tree_node('rbracket', [], ']')
        ]
    else:  # Array parameter with size
        p[0] = ASTNode('Param', value={'type': p[1], 'name': p[2], 'is_array': True, 'size': p[4]})
        children = [
            make_parse_tree_node('type', [], p[1]),
            make_parse_tree_node('id', [], p[2]),
            make_parse_tree_node('lbracket', [], '['),
            make_parse_tree_node('number', [], p[4]),
            make_parse_tree_node('rbracket', [], ']')
        ]
    p.slice[0].parse_tree = make_parse_tree_node('param', children)

# Block and statement lists
# ------------------------
# Handles code blocks and lists of statements.

def p_block(p):
    'block : LBRACE statements RBRACE'
    p[0] = ASTNode('Block', children=p[2])
    p.slice[0].parse_tree = make_parse_tree_node('block', [
        None,
        getattr(p.slice[2], 'parse_tree', None),
        None
    ])

def p_statements_multi(p):
    'statements : statements statement'
    p[0] = p[1] + [p[2]]
    p.slice[0].parse_tree = make_parse_tree_node('statements', [
        getattr(p.slice[1], 'parse_tree', None),
        getattr(p.slice[2], 'parse_tree', None)
    ])

def p_statements_single(p):
    'statements : statement'
    p[0] = [p[1]]
    p.slice[0].parse_tree = make_parse_tree_node('statements', [getattr(p.slice[1], 'parse_tree', None)])

def p_statements_empty(p):
    'statements : empty'
    p[0] = []
    p.slice[0].parse_tree = make_parse_tree_node('statements', [getattr(p.slice[1], 'parse_tree', None)])

# Statements
# ----------
# Handles variable declarations, assignments, control flow, and return statements.

def p_statement_declaration(p):
    '''statement : type ID ASSIGN expr SEMICOLON
                 | type ID SEMICOLON'''
    if len(p) == 6:
        p[0] = ASTNode('Declaration', value={'type': p[1], 'name': p[2]}, children=[p[4]])
        children = [
            make_parse_tree_node('type', [], p[1]),
            make_parse_tree_node('id', [], p[2]),
            make_parse_tree_node('assign', [], '='),
            get_parse_tree(p.slice[4]),
            make_parse_tree_node('semicolon', [], ';')
        ]
    else:
        p[0] = ASTNode('Declaration', value={'type': p[1], 'name': p[2]})
        children = [
            make_parse_tree_node('type', [], p[1]),
            make_parse_tree_node('id', [], p[2]),
            make_parse_tree_node('semicolon', [], ';')
        ]
    p.slice[0].parse_tree = make_parse_tree_node('declaration', children)

def p_statement_assignment(p):
    'statement : ID ASSIGN expr SEMICOLON'
    p[0] = ASTNode('Assignment', value={'name': p[1]}, children=[p[3]])
    children = [
        make_parse_tree_node('id', [], p[1]),
        make_parse_tree_node('assign', [], '='),
        get_parse_tree(p.slice[3]),
        make_parse_tree_node('semicolon', [], ';')
    ]
    p.slice[0].parse_tree = make_parse_tree_node('assignment', children)

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
    children = [
        make_parse_tree_node('return', [], 'return'),
        get_parse_tree(p.slice[2]),
        make_parse_tree_node('semicolon', [], ';')
    ]
    p.slice[0].parse_tree = make_parse_tree_node('return', children)

def p_statement_expr(p):
    'statement : expr SEMICOLON'
    p[0] = p[1]
    p.slice[0].parse_tree = make_parse_tree_node('expr_stmt', [getattr(p.slice[1], 'parse_tree', None), None])

def p_statement_for(p):
    '''statement : FOR LPAREN for_init SEMICOLON expr SEMICOLON for_update RPAREN statement'''
    p[0] = ASTNode('ForLoop', children=[
        p[3],  # initialization
        p[5],  # condition
        p[7],  # update
        p[9]   # body
    ])
    p.slice[0].parse_tree = make_parse_tree_node('for_loop', [
        getattr(p.slice[3], 'parse_tree', None),
        getattr(p.slice[5], 'parse_tree', None),
        getattr(p.slice[7], 'parse_tree', None),
        getattr(p.slice[9], 'parse_tree', None)
    ])

def p_for_init(p):
    '''for_init : type ID ASSIGN expr
                | ID ASSIGN expr
                | empty'''
    if len(p) == 5:
        p[0] = ASTNode('ForInit', value=p[1], children=[
            ASTNode('Variable', value=p[2]),
            p[4]
        ])
        p.slice[0].parse_tree = make_parse_tree_node('for_init', [
            getattr(p.slice[1], 'parse_tree', None),
            None,
            None,
            getattr(p.slice[4], 'parse_tree', None)
        ])
    elif len(p) == 4:
        p[0] = ASTNode('ForInit', children=[
            ASTNode('Variable', value=p[1]),
            p[3]
        ])
        p.slice[0].parse_tree = make_parse_tree_node('for_init', [
            None,
            None,
            getattr(p.slice[3], 'parse_tree', None)
        ])
    else:
        p[0] = ASTNode('ForInit')
        p.slice[0].parse_tree = make_parse_tree_node('for_init', [
            getattr(p.slice[1], 'parse_tree', None)
        ])

def p_for_update(p):
    '''for_update : ID INCREMENT
                 | ID DECREMENT
                 | ID ASSIGN expr
                 | empty'''
    if len(p) == 3:
        p[0] = ASTNode('ForUpdate', value=p[2], children=[
            ASTNode('Variable', value=p[1])
        ])
        p.slice[0].parse_tree = make_parse_tree_node('for_update', [None, None])
    elif len(p) == 4:
        p[0] = ASTNode('ForUpdate', children=[
            ASTNode('Variable', value=p[1]),
            p[3]
        ])
        p.slice[0].parse_tree = make_parse_tree_node('for_update', [None, None, getattr(p.slice[3], 'parse_tree', None)])
    else:
        p[0] = ASTNode('ForUpdate')
        p.slice[0].parse_tree = make_parse_tree_node('for_update', [getattr(p.slice[1], 'parse_tree', None)])

# Types
# -----
# Handles basic types (int, float, char).

def p_type(p):
    '''type : INT
            | FLOAT
            | CHAR'''
    p[0] = p[1]
    p.slice[0].parse_tree = make_parse_tree_node('type', [], p[1])

# Expressions and terms
# ---------------------
# Handles arithmetic, relational, and unary expressions.

def p_expr_term(p):
    'expr : term'
    p[0] = p[1]
    p.slice[0].parse_tree = make_parse_tree_node('expr_term', [getattr(p.slice[1], 'parse_tree', None)])

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

def p_expr_increment(p):
    '''expr : ID INCREMENT
            | ID DECREMENT'''
    p[0] = ASTNode('UnaryOp', value=p[2], children=[
        ASTNode('Variable', value=p[1])
    ])
    p.slice[0].parse_tree = make_parse_tree_node('unary_op', [None, None])

def p_term_binop(p):
    '''term : term MULTIPLY factor
            | term DIVIDE factor'''
    p[0] = ASTNode('BinaryOp', value=p[2], children=[p[1], p[3]])
    p.slice[0].parse_tree = make_parse_tree_node('binop', [getattr(p.slice[1], 'parse_tree', None), None, getattr(p.slice[3], 'parse_tree', None)])

def p_term_factor(p):
    'term : factor'
    p[0] = p[1]
    p.slice[0].parse_tree = make_parse_tree_node('term_factor', [getattr(p.slice[1], 'parse_tree', None)])

def p_factor(p):
    '''factor : NUMBER
              | STRING
              | ID
              | LPAREN expr RPAREN
              | ID LPAREN args RPAREN'''
    if len(p) == 2:
        if isinstance(p[1], int):
            p[0] = ASTNode('Number', value=p[1])
            p.slice[0].parse_tree = make_parse_tree_node('number', [], p[1])
        elif isinstance(p[1], str):
            if p.slice[1].type == 'STRING':
                p[0] = ASTNode('String', value=p[1])
                p.slice[0].parse_tree = make_parse_tree_node('string', [], p[1])
            else:
                p[0] = ASTNode('Variable', value=p[1])
                p.slice[0].parse_tree = make_parse_tree_node('id', [], p[1])
    elif len(p) == 4:
        # Parenthesized expression
        p[0] = p[2]
        p.slice[0].parse_tree = make_parse_tree_node('paren', [
            get_parse_tree(p.slice[1]),
            get_parse_tree(p.slice[2]),
            get_parse_tree(p.slice[3])
        ])
    elif len(p) == 5:  # Function call
        p[0] = ASTNode('Call', value=p[1], children=p[3])
        p.slice[0].parse_tree = make_parse_tree_node('call', [
            make_parse_tree_node('id', [], p[1]),
            make_parse_tree_node('lparen', [], '('),
            get_parse_tree(p.slice[3]),
            make_parse_tree_node('rparen', [], ')')
        ])

# Empty and argument rules
# ------------------------
# Handles empty productions and function call arguments.

def p_empty(p):
    'empty :'
    p[0] = None
    p.slice[0].parse_tree = make_parse_tree_node('empty', [])

def p_args_multi(p):
    'args : args COMMA expr'
    p[0] = p[1] + [p[3]]
    children = [
        get_parse_tree(p.slice[1]),
        make_parse_tree_node('comma', [], ','),
        get_parse_tree(p.slice[3])
    ]
    p.slice[0].parse_tree = make_parse_tree_node('args', children)

def p_args_single(p):
    'args : expr'
    p[0] = [p[1]]
    children = [get_parse_tree(p.slice[1])]
    p.slice[0].parse_tree = make_parse_tree_node('args', children)

def p_args_empty(p):
    'args : empty'
    p[0] = []
    p.slice[0].parse_tree = make_parse_tree_node('args', [])

# Error handling
# --------------
# Handles syntax errors and provides helpful messages.

def p_error(p):
    if p is None:
        print("Syntax error: Unexpected end of file")
        print("This usually means you're missing a closing brace '}' or parenthesis ')'")
        return
    
    print(f"Syntax error at '{p.value}'")
    print(f"Line {p.lineno}, position {p.lexpos}")
    print("Expected one of: ", end="")
    for state in parser.statestack:
        for item in state:
            if item.type == 'error':
                continue
            if item.type.startswith('p_'):
                continue
            print(f"'{item.type}'", end=", ")
    print()

parser = yacc.yacc(debug=True, write_tables=False)

def parse(input_text):
    try:
        result = parser.parse(input_text, tracking=True)
        if result is None:
            print("Error: Parser returned None")
            return None
        return result
    except Exception as e:
        print(f"Error during parsing: {str(e)}")
        return None

def parse_with_tree(code):
    global parse_tree_root
    parse_tree_root = None
    ast = parser.parse(code)
    # Fix: wrap in Program node if ast is a list
    if isinstance(ast, list):
        ast = ASTNode('Program', children=ast)
    return ast, parse_tree_root 

def ast_to_text(node, prefix='', is_last=True):
    if node is None:
        return ''
    lines = []
    connector = '└── ' if is_last else '├── '
    node_label = node.type
    if node.value is not None:
        if isinstance(node.value, dict):
            for k, v in node.value.items():
                node_label += f"\n{prefix}{'    ' if is_last else '│   '}{k}: {repr(v)}"
        else:
            node_label += f": {repr(node.value)}"
    lines.append(f"{prefix}{connector}{node_label}")
    child_prefix = prefix + ('    ' if is_last else '│   ')
    children = getattr(node, 'children', [])
    for i, child in enumerate(children):
        if child is None:
            continue  # Skip None children
        is_child_last = (i == len(children) - 1)
        child_text = ast_to_text(child, child_prefix, is_child_last)
        if child_text:  # Only append non-empty strings
            lines.append(child_text)
    return '\n'.join([line for line in lines if line and line.strip() not in ['└──', '├──']])

def parse_tree_to_text(node, prefix='', is_last=True):
    if node is None:
        return ''
    lines = []
    connector = '└── ' if is_last else '├── '
    node_label = node.rule
    if node.value is not None:
        node_label += f" ({node.value})"
    lines.append(f"{prefix}{connector}{node_label}")
    child_prefix = prefix + ('    ' if is_last else '│   ')
    children = getattr(node, 'children', [])
    for i, child in enumerate(children):
        if child is None:
            continue  # Skip None children
        is_child_last = (i == len(children) - 1)
        child_text = parse_tree_to_text(child, child_prefix, is_child_last)
        if child_text:  # Only append non-empty strings
            lines.append(child_text)
    return '\n'.join([line for line in lines if line and line.strip() not in ['└──', '├──']])
