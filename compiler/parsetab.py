
# parsetab.py
# This file is automatically generated. Do not edit.
# pylint: disable=W,C,R
_tabversion = '3.10'

_lr_method = 'LALR'

_lr_signature = 'ASSIGN CHAR COMMA DIVIDE ELSE EQ FLOAT GE GT ID IF INT LBRACE LE LPAREN LT MINUS MULTIPLY NEQ NUMBER PLUS RBRACE RETURN RPAREN SEMICOLON WHILEprogram : external_declarationsexternal_declarations : external_declarations external_declarationexternal_declarations : external_declarationexternal_declaration : type ID LPAREN params RPAREN blockexternal_declaration : statementparams : params COMMA paramparams : paramparams : param : type IDblock : LBRACE statements RBRACEstatements : statements statementstatements : statementstatement : type ID ASSIGN expr SEMICOLON\n                 | type ID SEMICOLONstatement : ID ASSIGN expr SEMICOLONstatement : blockstatement : IF LPAREN expr RPAREN statementstatement : IF LPAREN expr RPAREN statement ELSE statementstatement : WHILE LPAREN expr RPAREN statementstatement : RETURN expr SEMICOLONstatement : expr SEMICOLONtype : INT\n            | FLOAT\n            | CHARexpr : expr PLUS term\n            | expr MINUS termexpr : expr LT term\n            | expr GT term\n            | expr LE term\n            | expr GE term\n            | expr EQ term\n            | expr NEQ termexpr : termterm : term MULTIPLY factor\n            | term DIVIDE factorterm : factorfactor : NUMBERfactor : IDfactor : ID LPAREN args RPARENargs : args COMMA exprargs : exprargs : factor : LPAREN expr RPAREN'
    
_lr_action_items = {'INT':([0,2,3,7,8,16,20,26,38,39,43,45,60,61,62,70,73,74,77,78,80,81,82,84,85,],[9,9,-3,-16,-5,9,-2,-21,9,-12,9,-14,-20,-10,-11,-15,9,9,9,-13,-17,-19,-4,9,-18,]),'FLOAT':([0,2,3,7,8,16,20,26,38,39,43,45,60,61,62,70,73,74,77,78,80,81,82,84,85,],[10,10,-3,-16,-5,10,-2,-21,10,-12,10,-14,-20,-10,-11,-15,10,10,10,-13,-17,-19,-4,10,-18,]),'CHAR':([0,2,3,7,8,16,20,26,38,39,43,45,60,61,62,70,73,74,77,78,80,81,82,84,85,],[11,11,-3,-16,-5,11,-2,-21,11,-12,11,-14,-20,-10,-11,-15,11,11,11,-13,-17,-19,-4,11,-18,]),'ID':([0,2,3,4,6,7,8,9,10,11,15,16,20,22,23,26,27,28,29,30,31,32,33,34,35,36,38,39,40,41,42,44,45,60,61,62,66,70,72,73,74,78,80,81,82,84,85,],[5,5,-3,21,25,-16,-5,-22,-23,-24,25,5,-2,25,25,-21,25,25,25,25,25,25,25,25,25,25,5,-12,63,25,25,25,-14,-20,-10,-11,75,-15,25,5,5,-13,-17,-19,-4,5,-18,]),'IF':([0,2,3,7,8,16,20,26,38,39,45,60,61,62,70,73,74,78,80,81,82,84,85,],[13,13,-3,-16,-5,13,-2,-21,13,-12,-14,-20,-10,-11,-15,13,13,-13,-17,-19,-4,13,-18,]),'WHILE':([0,2,3,7,8,16,20,26,38,39,45,60,61,62,70,73,74,78,80,81,82,84,85,],[14,14,-3,-16,-5,14,-2,-21,14,-12,-14,-20,-10,-11,-15,14,14,-13,-17,-19,-4,14,-18,]),'RETURN':([0,2,3,7,8,16,20,26,38,39,45,60,61,62,70,73,74,78,80,81,82,84,85,],[15,15,-3,-16,-5,15,-2,-21,15,-12,-14,-20,-10,-11,-15,15,15,-13,-17,-19,-4,15,-18,]),'LBRACE':([0,2,3,7,8,16,20,26,38,39,45,60,61,62,70,73,74,76,78,80,81,82,84,85,],[16,16,-3,-16,-5,16,-2,-21,16,-12,-14,-20,-10,-11,-15,16,16,16,-13,-17,-19,-4,16,-18,]),'NUMBER':([0,2,3,6,7,8,15,16,20,22,23,26,27,28,29,30,31,32,33,34,35,36,38,39,41,42,44,45,60,61,62,70,72,73,74,78,80,81,82,84,85,],[19,19,-3,19,-16,-5,19,19,-2,19,19,-21,19,19,19,19,19,19,19,19,19,19,19,-12,19,19,19,-14,-20,-10,-11,-15,19,19,19,-13,-17,-19,-4,19,-18,]),'LPAREN':([0,2,3,5,6,7,8,13,14,15,16,20,21,22,23,25,26,27,28,29,30,31,32,33,34,35,36,38,39,41,42,44,45,60,61,62,70,72,73,74,78,80,81,82,84,85,],[6,6,-3,23,6,-16,-5,35,36,6,6,-2,43,6,6,23,-21,6,6,6,6,6,6,6,6,6,6,6,-12,6,6,6,-14,-20,-10,-11,-15,6,6,6,-13,-17,-19,-4,6,-18,]),'$end':([1,2,3,7,8,20,26,45,60,61,70,78,80,81,82,85,],[0,-1,-3,-16,-5,-2,-21,-14,-20,-10,-15,-13,-17,-19,-4,-18,]),'ASSIGN':([5,21,63,],[22,44,44,]),'MULTIPLY':([5,17,18,19,25,49,50,51,52,53,54,55,56,57,64,65,71,],[-38,41,-36,-37,-38,-43,41,41,41,41,41,41,41,41,-34,-35,-39,]),'DIVIDE':([5,17,18,19,25,49,50,51,52,53,54,55,56,57,64,65,71,],[-38,42,-36,-37,-38,-43,42,42,42,42,42,42,42,42,-34,-35,-39,]),'SEMICOLON':([5,12,17,18,19,21,25,37,46,49,50,51,52,53,54,55,56,57,63,64,65,69,71,],[-38,26,-33,-36,-37,45,-38,60,70,-43,-25,-26,-27,-28,-29,-30,-31,-32,45,-34,-35,78,-39,]),'PLUS':([5,12,17,18,19,24,25,37,46,48,49,50,51,52,53,54,55,56,57,58,59,64,65,69,71,79,],[-38,27,-33,-36,-37,27,-38,27,27,27,-43,-25,-26,-27,-28,-29,-30,-31,-32,27,27,-34,-35,27,-39,27,]),'MINUS':([5,12,17,18,19,24,25,37,46,48,49,50,51,52,53,54,55,56,57,58,59,64,65,69,71,79,],[-38,28,-33,-36,-37,28,-38,28,28,28,-43,-25,-26,-27,-28,-29,-30,-31,-32,28,28,-34,-35,28,-39,28,]),'LT':([5,12,17,18,19,24,25,37,46,48,49,50,51,52,53,54,55,56,57,58,59,64,65,69,71,79,],[-38,29,-33,-36,-37,29,-38,29,29,29,-43,-25,-26,-27,-28,-29,-30,-31,-32,29,29,-34,-35,29,-39,29,]),'GT':([5,12,17,18,19,24,25,37,46,48,49,50,51,52,53,54,55,56,57,58,59,64,65,69,71,79,],[-38,30,-33,-36,-37,30,-38,30,30,30,-43,-25,-26,-27,-28,-29,-30,-31,-32,30,30,-34,-35,30,-39,30,]),'LE':([5,12,17,18,19,24,25,37,46,48,49,50,51,52,53,54,55,56,57,58,59,64,65,69,71,79,],[-38,31,-33,-36,-37,31,-38,31,31,31,-43,-25,-26,-27,-28,-29,-30,-31,-32,31,31,-34,-35,31,-39,31,]),'GE':([5,12,17,18,19,24,25,37,46,48,49,50,51,52,53,54,55,56,57,58,59,64,65,69,71,79,],[-38,32,-33,-36,-37,32,-38,32,32,32,-43,-25,-26,-27,-28,-29,-30,-31,-32,32,32,-34,-35,32,-39,32,]),'EQ':([5,12,17,18,19,24,25,37,46,48,49,50,51,52,53,54,55,56,57,58,59,64,65,69,71,79,],[-38,33,-33,-36,-37,33,-38,33,33,33,-43,-25,-26,-27,-28,-29,-30,-31,-32,33,33,-34,-35,33,-39,33,]),'NEQ':([5,12,17,18,19,24,25,37,46,48,49,50,51,52,53,54,55,56,57,58,59,64,65,69,71,79,],[-38,34,-33,-36,-37,34,-38,34,34,34,-43,-25,-26,-27,-28,-29,-30,-31,-32,34,34,-34,-35,34,-39,34,]),'RBRACE':([7,26,38,39,45,60,61,62,70,78,80,81,85,],[-16,-21,61,-12,-14,-20,-10,-11,-15,-13,-17,-19,-18,]),'ELSE':([7,26,45,60,61,70,78,80,81,85,],[-16,-21,-14,-20,-10,-15,-13,84,-19,-18,]),'RPAREN':([17,18,19,23,24,25,43,47,48,49,50,51,52,53,54,55,56,57,58,59,64,65,67,68,71,75,79,83,],[-33,-36,-37,-42,49,-38,-8,71,-41,-43,-25,-26,-27,-28,-29,-30,-31,-32,73,74,-34,-35,76,-7,-39,-9,-40,-6,]),'COMMA':([17,18,19,23,25,43,47,48,49,50,51,52,53,54,55,56,57,64,65,67,68,71,75,79,83,],[-33,-36,-37,-42,-38,-8,72,-41,-43,-25,-26,-27,-28,-29,-30,-31,-32,-34,-35,77,-7,-39,-9,-40,-6,]),}

_lr_action = {}
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = {}
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'program':([0,],[1,]),'external_declarations':([0,],[2,]),'external_declaration':([0,2,],[3,20,]),'type':([0,2,16,38,43,73,74,77,84,],[4,4,40,40,66,40,40,66,40,]),'block':([0,2,16,38,73,74,76,84,],[7,7,7,7,7,7,82,7,]),'statement':([0,2,16,38,73,74,84,],[8,8,39,62,80,81,85,]),'expr':([0,2,6,15,16,22,23,35,36,38,44,72,73,74,84,],[12,12,24,37,12,46,48,58,59,12,69,79,12,12,12,]),'term':([0,2,6,15,16,22,23,27,28,29,30,31,32,33,34,35,36,38,44,72,73,74,84,],[17,17,17,17,17,17,17,50,51,52,53,54,55,56,57,17,17,17,17,17,17,17,17,]),'factor':([0,2,6,15,16,22,23,27,28,29,30,31,32,33,34,35,36,38,41,42,44,72,73,74,84,],[18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,64,65,18,18,18,18,18,]),'statements':([16,],[38,]),'args':([23,],[47,]),'params':([43,],[67,]),'param':([43,77,],[68,83,]),}

_lr_goto = {}
for _k, _v in _lr_goto_items.items():
   for _x, _y in zip(_v[0], _v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = {}
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> program","S'",1,None,None,None),
  ('program -> external_declarations','program',1,'p_program','lalr_parser.py',112),
  ('external_declarations -> external_declarations external_declaration','external_declarations',2,'p_external_declarations_multi','lalr_parser.py',118),
  ('external_declarations -> external_declaration','external_declarations',1,'p_external_declarations_single','lalr_parser.py',123),
  ('external_declaration -> type ID LPAREN params RPAREN block','external_declaration',6,'p_external_declaration_function','lalr_parser.py',128),
  ('external_declaration -> statement','external_declaration',1,'p_external_declaration_statement','lalr_parser.py',133),
  ('params -> params COMMA param','params',3,'p_params_multi','lalr_parser.py',138),
  ('params -> param','params',1,'p_params_single','lalr_parser.py',143),
  ('params -> <empty>','params',0,'p_params_empty','lalr_parser.py',148),
  ('param -> type ID','param',2,'p_param','lalr_parser.py',153),
  ('block -> LBRACE statements RBRACE','block',3,'p_block','lalr_parser.py',158),
  ('statements -> statements statement','statements',2,'p_statements_multi','lalr_parser.py',163),
  ('statements -> statement','statements',1,'p_statements_single','lalr_parser.py',168),
  ('statement -> type ID ASSIGN expr SEMICOLON','statement',5,'p_statement_declaration','lalr_parser.py',173),
  ('statement -> type ID SEMICOLON','statement',3,'p_statement_declaration','lalr_parser.py',174),
  ('statement -> ID ASSIGN expr SEMICOLON','statement',4,'p_statement_assignment','lalr_parser.py',188),
  ('statement -> block','statement',1,'p_statement_block','lalr_parser.py',196),
  ('statement -> IF LPAREN expr RPAREN statement','statement',5,'p_statement_if','lalr_parser.py',201),
  ('statement -> IF LPAREN expr RPAREN statement ELSE statement','statement',7,'p_statement_if_else','lalr_parser.py',206),
  ('statement -> WHILE LPAREN expr RPAREN statement','statement',5,'p_statement_while','lalr_parser.py',211),
  ('statement -> RETURN expr SEMICOLON','statement',3,'p_statement_return','lalr_parser.py',216),
  ('statement -> expr SEMICOLON','statement',2,'p_statement_expr','lalr_parser.py',221),
  ('type -> INT','type',1,'p_type','lalr_parser.py',226),
  ('type -> FLOAT','type',1,'p_type','lalr_parser.py',227),
  ('type -> CHAR','type',1,'p_type','lalr_parser.py',228),
  ('expr -> expr PLUS term','expr',3,'p_expr_binop','lalr_parser.py',233),
  ('expr -> expr MINUS term','expr',3,'p_expr_binop','lalr_parser.py',234),
  ('expr -> expr LT term','expr',3,'p_expr_relop','lalr_parser.py',239),
  ('expr -> expr GT term','expr',3,'p_expr_relop','lalr_parser.py',240),
  ('expr -> expr LE term','expr',3,'p_expr_relop','lalr_parser.py',241),
  ('expr -> expr GE term','expr',3,'p_expr_relop','lalr_parser.py',242),
  ('expr -> expr EQ term','expr',3,'p_expr_relop','lalr_parser.py',243),
  ('expr -> expr NEQ term','expr',3,'p_expr_relop','lalr_parser.py',244),
  ('expr -> term','expr',1,'p_expr_term','lalr_parser.py',249),
  ('term -> term MULTIPLY factor','term',3,'p_term_binop','lalr_parser.py',254),
  ('term -> term DIVIDE factor','term',3,'p_term_binop','lalr_parser.py',255),
  ('term -> factor','term',1,'p_term_factor','lalr_parser.py',260),
  ('factor -> NUMBER','factor',1,'p_factor_number','lalr_parser.py',265),
  ('factor -> ID','factor',1,'p_factor_id','lalr_parser.py',270),
  ('factor -> ID LPAREN args RPAREN','factor',4,'p_factor_call','lalr_parser.py',275),
  ('args -> args COMMA expr','args',3,'p_args_multi','lalr_parser.py',280),
  ('args -> expr','args',1,'p_args_single','lalr_parser.py',285),
  ('args -> <empty>','args',0,'p_args_empty','lalr_parser.py',290),
  ('factor -> LPAREN expr RPAREN','factor',3,'p_factor_paren','lalr_parser.py',295),
]
