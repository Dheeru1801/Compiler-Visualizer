from flask import Flask, render_template, request, jsonify
from compiler.lexer import Lexer

# from compiler.lalr_parser import parse_with_tree, ASTNode, ParseTreeNode
from compiler.lalr_parser import parse_with_tree, ASTNode, ParseTreeNode, ast_to_text, parse_tree_to_text
from compiler.semantic_analyzer import SemanticAnalyzer
from compiler.ir_generator import generate_ir
import pydot
import io
import pprint
import json
import compiler.parsetab as parsetab
import traceback

app = Flask(__name__)

def flatten_children(children):
    for child in children:
        if isinstance(child, list):
            yield from flatten_children(child)
        else:
            yield child

def create_tree_graph(node, graph=None, parent=None, node_id=0, is_parse_tree=False):
    if node is None:
        return graph or pydot.Dot(graph_type='digraph')
    
    if graph is None:
        graph = pydot.Dot(graph_type='digraph')
        graph.set_rankdir('TB')
    
    current_id = str(node_id)
    
    try:
        if is_parse_tree:
            label = node.rule
            if node.value is not None:
                label += f" ({node.value})"
        else:
            label = f"{node.type}"
            if node.value:
                label += f": {node.value}"
                
        node_dot = pydot.Node(current_id, label=label)
        graph.add_node(node_dot)
        
        if parent is not None:
            edge = pydot.Edge(parent, current_id)
            graph.add_edge(edge)
            
        children = getattr(node, 'children', [])
        if children:
            for i, child in enumerate(flatten_children(children)):
                if child is not None:
                    if is_parse_tree and not hasattr(child, 'rule'):
                        continue  # skip non-parse-tree nodes
                    create_tree_graph(child, graph, current_id, node_id * 10 + i + 1, is_parse_tree)
    except Exception as e:
        print(f"Error in create_tree_graph: {e}")
        traceback.print_exc()
        
    return graph

def get_parse_table():
    actions = getattr(parsetab, '_lr_action', {})
    gotos = getattr(parsetab, '_lr_goto', {})
    return {
        'action': actions,
        'goto': gotos
    }

def safe_text_generation(node, func, default_msg):
    """Safely generate text representation with comprehensive error handling"""
    if node is None:
        return default_msg
    
    try:
        result = func(node)
        if result is None:
            return default_msg
        return result
    except Exception as e:
        print(f"Error generating text: {str(e)}")
        traceback.print_exc()
        return f"{default_msg}: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        code = request.json.get('code', '')
        # Lexical Analysis (for tokens display only)
        lexer = Lexer(code)
        tokens = lexer.tokenize()

        # Syntax Analysis (LALR, both AST and parse tree)
        ast, parse_tree = parse_with_tree(code)
        if ast is None:
            return jsonify({'error': 'Failed to generate AST'}), 400

        # Semantic Analysis
        analyzer = SemanticAnalyzer()
        symbol_table = analyzer.analyze(ast)

        # Generate AST and Parse Tree visualizations
        try:
            ast_graph = create_tree_graph(ast)
            ast_svg = ast_graph.create_svg().decode('utf-8')
        except Exception as e:
            print(f"Error generating AST SVG: {e}")
            traceback.print_exc()
            ast_svg = f'<svg width="300" height="100"><text x="10" y="50" fill="red">Error generating AST: {str(e)}</text></svg>'

        try:
            parse_tree_graph = create_tree_graph(parse_tree, is_parse_tree=True)
            parse_tree_svg = parse_tree_graph.create_svg().decode('utf-8')
        except Exception as e:
            print(f"Error generating Parse Tree SVG: {e}")
            traceback.print_exc()
            parse_tree_svg = f'<svg width="300" height="100"><text x="10" y="50" fill="red">Error generating Parse Tree: {str(e)}</text></svg>'
        
        # Add AST to_dict output as pretty JSON
        try:
            ast_dict = ast.to_dict() if hasattr(ast, 'to_dict') else {}
        except Exception as e:
            print(f"Error generating AST dict: {e}")
            traceback.print_exc()
            ast_dict = {"error": str(e)}
            
        # Add parse table
        parse_table = get_parse_table()
        
        # Generate IR
        try:
            ir = generate_ir(ast)
        except Exception as e:
            print(f"Error generating IR: {e}")
            traceback.print_exc()
            ir = [f"Error generating IR: {str(e)}"]

        # Generate text representations using our safer function
        ast_text = safe_text_generation(ast, ast_to_text, "Unable to generate AST text representation")
        parse_tree_text = safe_text_generation(parse_tree, parse_tree_to_text, "Unable to generate parse tree text representation")
            
        return jsonify({
            'tokens': [token.to_dict() for token in tokens],
            'ast_svg': ast_svg,
            'parse_tree_svg': parse_tree_svg,
            'symbol_table': symbol_table,
            'ast_dict': ast_dict,
            'parse_table': parse_table,
            'ir': ir,
            'ast_text': ast_text,
            'parse_tree_text': parse_tree_text
        })
    except Exception as e:
        print(f"General error during analysis: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)

