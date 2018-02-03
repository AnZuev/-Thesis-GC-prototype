
import javalang.javalang as javalang
from libs import *
from process.flow import *
from process.types_manager import *

program = read_program("program.java")
tree = javalang.parse.parse(program)

init_types_manager(tree)

flow_graph = init_raw_flow_graph(tree)

f = 3
#tokens = javalang.tokenizer.tokenize('System.out.println("Hello " + "world");')
#parser = javalang.parser.Parser(tokens)
#t = parser.parse_expression()
#f = 4


