# -----------------------------
# IR GENERATOR MODULE
# -----------------------------
# This module generates intermediate representation (IR) code from the AST.
# The IR is a list of simple instructions for further compilation or analysis.

from compiler.lalr_parser import ASTNode

def generate_ir(ast):
    ir = []  # List to store IR instructions
    temp_counter = 0  # Counter for temporary variables
    label_counter = 0  # Counter for labels

    # Helper to generate a new temporary variable name
    def new_temp():
        nonlocal temp_counter
        temp_counter += 1
        return f"t{temp_counter}"

    # Helper to generate a new label name
    def new_label():
        nonlocal label_counter
        label_counter += 1
        return f"L{label_counter}"

    # Main recursive function to visit AST nodes and generate IR
    def visit(node):
        if node is None:
            return None
        # Program root: visit all children (top-level declarations)
        if node.type == 'Program':
            for child in node.children:
                visit(child)
            return None
        # Function definition: emit function header, visit body
        elif node.type == 'FunctionDef':
            func_name = "main"
            func_type = "int"
            if node.value and isinstance(node.value, dict):
                func_name = node.value.get('name', 'main')
                func_type = node.value.get('type', 'int')
            params = []
            if len(node.children) > 1:
                for child in node.children[:-1]:
                    if child.type == 'Param' and isinstance(child.value, dict):
                        param_name = child.value.get('name')
                        if param_name:
                            params.append(param_name)
            param_str = ", ".join(params)
            ir.append(f"function {func_name}({param_str}):")
            if node.children:
                visit(node.children[-1])  # Visit function body
            return None
        # Block: visit all statements in the block
        elif node.type == 'Block':
            for stmt in node.children:
                visit(stmt)
            return None
        # Variable declaration (with or without initialization)
        elif node.type == 'Declaration':
            if len(node.children) >= 1:
                var_node = ASTNode('Variable', value=node.value['name'])
                if node.children:
                    init_node = node.children[0]
                    if hasattr(init_node, 'type') and init_node.type == 'Number':
                        value = init_node.value
                        ir.append(f"{var_node.value} = {value}")
                    elif hasattr(init_node, 'type') and init_node.type == 'BinaryOp':
                        left = visit(init_node.children[0])
                        right = visit(init_node.children[1])
                        temp = new_temp()
                        op = init_node.value
                        ir.append(f"{temp} = {left} {op} {right}")
                        ir.append(f"{var_node.value} = {temp}")
                    elif hasattr(init_node, 'type') and init_node.type == 'Call':
                        func_name = init_node.value
                        args = []
                        for arg in init_node.children:
                            args.append(visit(arg))
                        temp = new_temp()
                        arg_str = ", ".join(args)
                        ir.append(f"{temp} = call {func_name}({arg_str})")
                        ir.append(f"{var_node.value} = {temp}")
                    else:
                        ir.append(f"{var_node.value} = 0")
            return None
        # Return statement
        elif node.type == 'Return':
            if node.children:
                value = visit(node.children[0])
                ir.append(f"return {value}")
            return None
        # Variable node: return its name
        elif node.type == 'Variable':
            return node.value
        # Number node: return its value
        elif node.type == 'Number':
            return node.value
        # Binary operation (arithmetic): generate IR for left/right, emit temp
        elif node.type == 'BinaryOp':
            left = visit(node.children[0])
            right = visit(node.children[1])
            temp = new_temp()
            op = node.value
            ir.append(f"{temp} = {left} {op} {right}")
            return temp
        # Relational operation: generate IR for left/right, emit temp
        elif node.type == 'RelOp':
            left = visit(node.children[0])
            right = visit(node.children[1])
            temp = new_temp()
            op = node.value
            ir.append(f"{temp} = {left} {op} {right}")
            return temp
        # Function call: generate IR for arguments, emit call
        elif node.type == 'Call':
            func_name = node.value
            args = []
            for arg in node.children:
                args.append(visit(arg))
            temp = new_temp()
            arg_str = ", ".join(args)
            ir.append(f"{temp} = call {func_name}({arg_str})")
            return temp
        # Assignment: emit assignment IR
        elif node.type == 'Assignment':
            name = node.value['name']
            value = visit(node.children[0])
            ir.append(f"{name} = {value}")
            return name
        # For loop: emit IR for init, condition, body, update, and jumps
        elif node.type == 'ForLoop':
            visit(node.children[0])  # Initialization
            loop_label = new_label()
            end_label = new_label()
            ir.append(f"{loop_label}:")
            cond_node = node.children[1]
            cond_temp = visit(cond_node)
            # If condition is a relational op or variable, use its value
            if cond_temp is None:
                if hasattr(cond_node, 'type'):
                    if cond_node.type == 'BinaryOp':
                        cond_temp = visit(cond_node)
                    elif cond_node.type == 'Variable':
                        cond_temp = cond_node.value
                    elif cond_node.type == 'Number':
                        cond_temp = cond_node.value
                    else:
                        cond_temp = f"unhandled_{cond_node.type}"
                else:
                    cond_temp = 'unhandled_cond'
            ir.append(f"if not {cond_temp} goto {end_label}")
            visit(node.children[3])  # Body
            visit(node.children[2])  # Update
            ir.append(f"goto {loop_label}")
            ir.append(f"{end_label}:")
            return None
        # Fallback for unknown node types
        else:
            if hasattr(node, 'type'):
                print(f"[IR WARNING] Unhandled node type: {node.type}")
            else:
                print(f"[IR WARNING] Unknown node: {node}")
            return None

    # Start IR generation from the root AST node
    visit(ast)
    return ir 
