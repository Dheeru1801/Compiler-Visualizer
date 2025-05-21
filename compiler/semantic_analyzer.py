class Symbol:
    def __init__(self, name, kind, type, scope, address=None, value=None, function=None, additional_info=None, size=None, dimensions=None):
        self.name = name
        self.kind = kind  # 'variable', 'function', 'array'
        self.type = type
        self.scope = scope
        self.address = address
        self.value = value
        self.function = function
        self.additional_info = additional_info
        self._array_values = {}  # Store array values as integers

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
    
    def next_address(self, size=4):
        addr = hex(self.memory_counter)
        self.memory_counter += size
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
        if isinstance(node, str):
            return node
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
        var_type = node.value['type']  # Access type from dictionary
        var_name = node.value['name']  # Access name from dictionary
        # Check if variable is already declared in this scope
        if self.symbol_table.lookup(var_name, self.current_function if scope == 'Local' else None):
            raise Exception(f'Variable {var_name} already declared')
        address = self.next_address()
        symbol = Symbol(var_name, 'variable', var_type, scope, address, function=self.current_function)
        if len(node.children) > 0:  # Has initialization
            value = self.visit(node.children[0], scope)
            symbol.value = value
        symbol.additional_info = f'Data type: {var_type}'
        self.symbol_table.define(symbol)
        self.all_symbols.append(symbol)
    
    def visit_Assignment(self, node, scope):
        if len(node.children) < 2:
            return
        
        var_name = node.value['name']  # Access name from dictionary
        symbol = self.symbol_table.lookup(var_name, self.current_function if scope == 'Local' else None)
        if not symbol:
            raise Exception(f'Undefined variable: {var_name}')
        
        value = self.visit(node.children[0], scope)
        
        # For array assignments
        if symbol.kind == 'array':
            # If this is an array access assignment (like numbers[i] = ...)
            if isinstance(node.children[0], ASTNode) and node.children[0].type == 'ArrayAccess':
                # Get the index from the array access
                index_node = node.children[0].children[0]
                index = self.visit(index_node, scope)
                
                # For symbolic indices, store the expression
                if isinstance(index, str):
                    symbol.value = f"{var_name}[{index}] = {value}"
                    return
                
                # For numeric indices, store the value
                if isinstance(index, int):
                    # Convert value to integer if possible
                    if isinstance(value, str) and value.isdigit():
                        value = int(value)
                    symbol.set_array_value(index, value)
                else:
                    symbol.value = f"{var_name}[{index}] = {value}"
            else:
                # For direct array assignments
                symbol.value = str(value)
        else:
            # For regular variables
            try:
                if isinstance(value, str):
                    if value.isdigit():
                        value = int(value)
                symbol.value = value
            except ValueError:
                symbol.value = str(value)
    
    def visit_BinaryOp(self, node, scope):
        if len(node.children) < 2:
            return None
        
        left = self.visit(node.children[0], scope)
        right = self.visit(node.children[1], scope)
        
        # If either operand is None, return a symbolic expression
        if left is None or right is None:
            return f"({left if left is not None else '?'} {node.value} {right if right is not None else '?'})"
        
        # If either operand is a symbolic expression (including array access), return symbolic
        if isinstance(left, str) or isinstance(right, str):
            # For array access, wrap in parentheses
            left_str = f"({left})" if isinstance(left, str) and '[' in left else str(left)
            right_str = f"({right})" if isinstance(right, str) and '[' in right else str(right)
            return f"({left_str} {node.value} {right_str})"
        
        # Both operands must be numeric for arithmetic
        if not (isinstance(left, (int, float)) and isinstance(right, (int, float))):
            return f"({left} {node.value} {right})"
        
        # Perform arithmetic operations
        if node.value == '+':
            return left + right
        elif node.value == '-':
            return left - right
        elif node.value == '*':
            return left * right
        elif node.value == '/':
            if right == 0:
                raise Exception("Division by zero")
            return left // right  # Use integer division for C-like behavior
    
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
        func_name = node.value['name']  # Access name from dictionary
        func_type = node.value['type']  # Access type from dictionary
        address = self.next_address()
        symbol = Symbol(func_name, 'function', func_type, 'Global', address, value='N/A', additional_info=f'Return type: {func_type}')
        self.symbol_table.define(symbol)
        self.all_symbols.append(symbol)
        old_symbols = self.symbol_table.symbols.copy()
        old_function = self.current_function
        self.current_function = func_name
        for param in param_nodes:
            if hasattr(param, 'type') and param.type == 'Param':
                pname = param.value['name']  # Access name from dictionary
                ptype = param.value['type']  # Access type from dictionary
                paddr = self.next_address()
                psymbol = Symbol(pname, 'parameter', ptype, 'Local', paddr, additional_info=f'Data type: {ptype}', function=func_name)
                self.symbol_table.define(psymbol)
                self.all_symbols.append(psymbol)
        if block_node:
            self.visit(block_node, scope='Local')
        self.symbol_table.symbols = old_symbols
        self.current_function = old_function 

    def visit_ForLoop(self, node, scope):
        # Create new scope for the loop
        loop_scope = f"{scope}_for"
        
        # Analyze initialization
        init = self.visit(node.children[0], loop_scope)
        
        # Analyze condition
        condition = self.visit(node.children[1], loop_scope)
        
        # Analyze update
        update = self.visit(node.children[2], loop_scope)
        
        # Analyze body
        body = self.visit(node.children[3], loop_scope)
        
        return {
            'init': init,
            'condition': condition,
            'update': update,
            'body': body
        }

    def visit_ForInit(self, node, scope):
        if not node.children:
            return None
        
        if len(node.children) == 2:  # Variable declaration
            var_type = self.visit(node.value, scope)
            var_name = node.children[0].value
            init_value = self.visit(node.children[1], scope)
            
            # Convert to integer if possible
            if isinstance(init_value, str):
                if init_value.isdigit():
                    init_value = int(init_value)
            
            symbol = Symbol(
                name=var_name,
                kind='variable',
                type=var_type,
                scope=scope,
                address=self.next_address(),
                value=init_value,
                function=self.current_function
            )
            self.symbol_table.define(symbol)
            self.all_symbols.append(symbol)
            return symbol
        else:  # Assignment
            var_name = node.children[0].value
            init_value = self.visit(node.children[1], scope)
            
            # Convert to integer if possible
            if isinstance(init_value, str):
                if init_value.isdigit():
                    init_value = int(init_value)
            
            symbol = self.symbol_table.lookup(var_name, self.current_function if scope == 'Local' else None)
            if not symbol:
                raise Exception(f'Undefined variable: {var_name}')
            
            symbol.value = init_value
            return symbol

    def visit_ForUpdate(self, node, scope):
        if not node.children:
            return None
        
        var_name = node.children[0].value
        symbol = self.symbol_table.lookup(var_name, self.current_function if scope == 'Local' else None)
        if not symbol:
            raise Exception(f'Undefined variable: {var_name}')
        
        if node.value in ('++', '--'):
            # Handle increment/decrement
            current_value = symbol.value
            
            # Initialize to 0 if None
            if current_value is None:
                current_value = 0
            
            # For symbolic values, return symbolic expression
            if isinstance(current_value, str):
                return f"{current_value}{node.value}"
            
            # Perform increment/decrement
            if node.value == '++':
                symbol.value = current_value + 1
            else:
                symbol.value = current_value - 1
        else:
            # Handle assignment
            new_value = self.visit(node.children[1], scope)
            if new_value is None:
                return None
            
            # Convert to integer if possible
            if isinstance(new_value, str):
                if new_value.isdigit():
                    new_value = int(new_value)
            symbol.value = new_value
        
        return symbol 
