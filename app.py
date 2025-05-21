from flask import Flask, render_template, request, jsonify
from compiler.lexer import Lexer

from compiler.lalr_parser import parse_with_tree, ASTNode, ParseTreeNode
from compiler.semantic_analyzer import SemanticAnalyzer
from compiler.ir_generator import generate_ir
import pydot
import io
import pprint
import json
import compiler.parsetab as parsetab

app = Flask(__name__)

def flatten_children(children):
    for child in children:
        if isinstance(child, list):
            yield from flatten_children(child)
        else:
            yield child

def create_tree_graph(node, graph=None, parent=None, node_id=0, is_parse_tree=False):
    if graph is None:
        graph = pydot.Dot(graph_type='digraph')
        graph.set_rankdir('TB')
    current_id = str(node_id)
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
    for i, child in enumerate(flatten_children(getattr(node, 'children', []))):
        if child is not None:
            if is_parse_tree and not hasattr(child, 'rule'):
                continue  # skip non-parse-tree nodes
            create_tree_graph(child, graph, current_id, node_id * 10 + i + 1, is_parse_tree)
    return graph

def get_parse_table():
    actions = getattr(parsetab, '_lr_action', {})
    gotos = getattr(parsetab, '_lr_goto', {})
    return {
        'action': actions,
        'goto': gotos
    }

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

        # Semantic Analysis
        analyzer = SemanticAnalyzer()
        symbol_table = analyzer.analyze(ast)

        # Generate AST and Parse Tree visualizations
        ast_graph = create_tree_graph(ast)
        ast_svg = ast_graph.create_svg().decode('utf-8')
        parse_tree_graph = create_tree_graph(parse_tree, is_parse_tree=True)
        parse_tree_svg = parse_tree_graph.create_svg().decode('utf-8')
        
        # Add AST to_dict output as pretty JSON
        ast_dict = ast.to_dict() if hasattr(ast, 'to_dict') else {}
        # Add parse table
        parse_table = get_parse_table()
        # Generate IR
        ir = generate_ir(ast)
        return jsonify({
            'tokens': [token.to_dict() for token in tokens],
            'ast_svg': ast_svg,
            'parse_tree_svg': parse_tree_svg,
            'symbol_table': symbol_table,
            'ast_dict': ast_dict,
            'parse_table': parse_table,
            'ir': ir
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True) 
    
