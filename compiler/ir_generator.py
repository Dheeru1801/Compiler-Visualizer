def generate_ir(ast):
    ir = []
    temp_counter = 0
    label_counter = 0

    def new_temp():
        nonlocal temp_counter
        temp_counter += 1
        return f"t{temp_counter}"

    def new_label():
        nonlocal label_counter
        label_counter += 1
        return f"L{label_counter}"

    def visit(node):
        if node is None:
            return None
        if node.type == 'Program':
            for child in node.children:
                visit(child)
            return None
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
                visit(node.children[-1])
            return None
        elif node.type == 'Block':
            for stmt in node.children:
                visit(stmt)
            return None
        elif node.type == 'Declaration':
            if len(node.children) >= 2:
                var_node = node.children[0]
                init_node = node.children[1]
                if var_node.type == 'Variable':
                    name = var_node.value
                    if init_node.type == 'Number':
                        value = init_node.value
                        ir.append(f"{name} = {value}")
                    elif init_node.type == 'BinaryOp':
                        left = visit(init_node.children[0])
                        right = visit(init_node.children[1])
                        temp = new_temp()
                        op = init_node.value
                        ir.append(f"{temp} = {left} {op} {right}")
                        ir.append(f"{name} = {temp}")
                    elif init_node.type == 'Call':
                        func_name = init_node.value
                        args = []
                        for arg in init_node.children:
                            args.append(visit(arg))
                        temp = new_temp()
                        arg_str = ", ".join(args)
                        ir.append(f"{temp} = call {func_name}({arg_str})")
                        ir.append(f"{name} = {temp}")
                    else:
                        ir.append(f"{name} = 0")
            return None
        elif node.type == 'Return':
            if node.children:
                value = visit(node.children[0])
                ir.append(f"return {value}")
            return None
        elif node.type == 'number':
            return node.value
        elif node.type == 'identifier':
            return node.value
        elif node.type == 'Variable':
            return node.value
        elif node.type == 'BinaryOp':
            left = visit(node.children[0])
            right = visit(node.children[1])
            temp = new_temp()
            op = node.value
            ir.append(f"{temp} = {left} {op} {right}")
            return temp
        elif node.type == 'Number':
            return node.value
        elif node.type == 'Call':
            func_name = node.value
            args = []
            for arg in node.children:
                args.append(visit(arg))
            temp = new_temp()
            arg_str = ", ".join(args)
            ir.append(f"{temp} = call {func_name}({arg_str})")
            return temp
        elif node.type == 'ParameterList':
            params = []
            for param in node.children:
                if param.type == 'Parameter':
                    param_name = param.children[0].value
                    params.append(param_name)
            return params
        elif node.type == 'Parameter':
            if node.children and node.children[0].type == 'Variable':
                return node.children[0].value
            return None
        elif node.type == 'assignment':
            name = node.children[0].value
            value = visit(node.children[1])
            ir.append(f"{name} = {value}")
            return name
    visit(ast)
    return ir 