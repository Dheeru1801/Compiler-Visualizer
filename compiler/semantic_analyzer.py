class Symbol:
    def __init__(self, name, kind, type, scope, address, value=None, additional_info=None, function=None):
        self.name = name
        self.kind = kind  # variable, constant, function, parameter
        self.type = type  # data type (int, float, etc.)
        self.scope = scope  # Global, Local
        self.address = address
        self.value = value
        self.additional_info = additional_info
        self.function = function  # function name if local/parameter

class SymbolTable:
    def __init__(self):
        self.symbols = {}
    
    def define(self, symbol):
        # Use (name, function) as key for Local/parameter, name for Global
        key = (symbol.name, symbol.function) if symbol.scope == 'Local' else symbol.name
        self.symbols[key] = symbol
    
    def lookup(self, name, function=None):
        # Try local first if function is given, else global
        if function:
            return self.symbols.get((name, function)) or self.symbols.get(name)
        return self.symbols.get(name)

class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.all_symbols = []  # Collect all symbols for display
        self.memory_counter = 0x1000
        self.current_function = None
    
    def next_address(self):
        addr = hex(self.memory_counter)
        self.memory_counter += 4
        return addr
    
    def analyze(self, ast):
        if not ast:
            return []
        self.visit(ast, scope='Global')
        # Return all symbols as a list of dicts for display
        return [
            {
                'name': s.name,
                'kind': s.kind,
                'type': s.type,
                'scope': s.scope,
                'address': s.address,
                'value': s.value if s.value is not None else ('Uninitialized' if s.kind == 'variable' else ('N/A' if s.kind == 'function' else '')),
                'function': s.function or '',
                'additional_info': s.additional_info or ''
            }
            for s in self.all_symbols
        ]
    
    def visit(self, node, scope='Global'):
        method_name = f'visit_{node.type}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node, scope)
    
    def generic_visit(self, node, scope):
        for child in getattr(node, 'children', []):
            self.visit(child, scope)
    
    def visit_Program(self, node, scope):
        for child in getattr(node, 'children', []):
            self.visit(child, scope)
    
    def visit_Block(self, node, scope):
        for child in getattr(node, 'children', []):
            self.visit(child, scope)
    
    def visit_Declaration(self, node, scope):
        if len(node.children) < 1:
            return
        var_type = node.value
        var_name = node.children[0].value
        # Check if variable is already declared in this scope
        if self.symbol_table.lookup(var_name, self.current_function if scope == 'Local' else None):
            raise Exception(f'Variable {var_name} already declared')
        address = self.next_address()
        symbol = Symbol(var_name, 'variable', var_type, scope, address, function=self.current_function)
        if len(node.children) > 1:
            value = self.visit(node.children[1], scope)
            symbol.value = value
        symbol.additional_info = f'Data type: {var_type}'
        self.symbol_table.define(symbol)
        self.all_symbols.append(symbol)
    
    def visit_Assignment(self, node, scope):
        if len(node.children) < 2:
            return
        var_name = node.children[0].value
        symbol = self.symbol_table.lookup(var_name, self.current_function if scope == 'Local' else None)
        if not symbol:
            raise Exception(f'Undefined variable: {var_name}')
        value = self.visit(node.children[1], scope)
        symbol.value = value
    
    def visit_BinaryOp(self, node, scope):
        if len(node.children) < 2:
            return None
        left = self.visit(node.children[0], scope)
        right = self.visit(node.children[1], scope)
        # If either operand is None, return a symbolic expression
        if left is None or right is None:
            return f"({left if left is not None else '?'} {node.value} {right if right is not None else '?'})"
        # If either operand is a string (symbolic), return a symbolic expression
        if isinstance(left, str) or isinstance(right, str):
            return f"({left} {node.value} {right})"
        if node.value == '+':
            return left + right
        elif node.value == '-':
            return left - right
        elif node.value == '*':
            return left * right
        elif node.value == '/':
            return left / right
    
    def visit_Number(self, node, scope):
        return int(node.value)
    
    def visit_Variable(self, node, scope):
        symbol = self.symbol_table.lookup(node.value, self.current_function if scope == 'Local' else None)
        if not symbol:
            raise Exception(f'Undefined variable: {node.value}')
        return symbol.value

    def visit_FunctionDef(self, node, scope):
        if not node.children:
            param_nodes = []
            block_node = None
        else:
            param_nodes = [child for child in node.children if getattr(child, 'type', None) == 'Param']
            block_node = node.children[-1] if node.children else None
        func_name = node.value['name']
        func_type = node.value['type']
        address = self.next_address()
        symbol = Symbol(func_name, 'function', func_type, 'Global', address, value='N/A', additional_info=f'Return type: {func_type}')
        self.symbol_table.define(symbol)
        self.all_symbols.append(symbol)
        old_symbols = self.symbol_table.symbols.copy()
        old_function = self.current_function
        self.current_function = func_name
        for param in param_nodes:
            if hasattr(param, 'type') and param.type == 'Param':
                pname = param.value['name']
                ptype = param.value['type']
                paddr = self.next_address()
                psymbol = Symbol(pname, 'parameter', ptype, 'Local', paddr, additional_info=f'Data type: {ptype}', function=func_name)
                self.symbol_table.define(psymbol)
                self.all_symbols.append(psymbol)
        if block_node:
            self.visit(block_node, scope='Local')
        self.symbol_table.symbols = old_symbols
        self.current_function = old_function 