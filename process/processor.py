from javalang.javalang.tree import *
from process.ds import Scope, Object, VariableAlias, Heap, ClassInfo
from process.flow import *

# flowGraph is ready
# now it is time to add processor itself, after that
# we will know what exactly happens inside methods


def process_expression(expression: LocalVariableDeclaration, scope: Scope, heap: Heap):
    if expression is BinaryOperation:
        pass
    elif isinstance(expression, LocalVariableDeclaration):
        return process_local_variable_declaration(expression, scope)
    elif expression is IfStatement:
        pass
    elif expression is ForStatement:
        pass
    elif expression is MethodInvocation:
        pass
    elif isinstance(expression, Literal):
        return process_literal(expression, scope)
    elif isinstance(expression, MemberReference):
        return process_member_reference(expression, scope)
    elif isinstance(expression, ClassCreator):
        return process_class_creator(expression, scope)
    elif isinstance(expression, ReturnStatement):
        return process_return_statemnet(expression, scope)
    elif isinstance(expression, Statementexpressionression):
        process_statement_expressionression(expression, scope)
    elif isinstance(expression, MethodInvocation):
        process_method_invocation(expression, scope)
    else:
        pass


# +++++++++++++++++ Variables declaration and initialization +++++++++++++++++

def process_local_variable_declaration(expression: LocalVariableDeclaration, scope: Scope, heap: Heap):
    var_type = expression.type.name
    for declarator in expression.declarators:
        obj = process_expression(declarator.initializer, scope, heap)
        variable = VariableAlias(declarator.name, obj, var_type)
        scope.add_local_variable(variable)


def process_literal(expression: Literal, scope: Scope, heap: Heap) -> Object:
    return heap.allocate_object()


def process_member_reference(expression: MemberReference, scope: Scope, heap: Heap) -> Object:
    var_alias = scope.get_local_variable(expression.member)
    return var_alias.get_object()


def process_class_creator(expression: ClassCreator, scope: Scope, heap: Heap) -> Object:
    obj = heap.allocate_object()
    for argument in expression.arguments:
        obj.add_refer(process_expression(argument, scope, heap))
    return obj


def init_object_of_class(heap: Heap, class_info: ClassInfo):
    pass


# +++++++++++++++++ Assignments +++++++++++++++++

def process_assignment(expression: Assignment, scope: Scope, heap: Heap):
    obj = process_expression(expression.value, scope, heap)
    # could be 3 possible cases:
    # - member reference is just a local variable ( a = 4 )
    # - member reference is a field of some object (a.b = 4)
    # - member reference is a result of some method execution ( a.get().field = 4 )
    if len(expression.expressionl.quelifier) == 0:
        # first case
        variable_alias = scope.get_local_variable(expression.expressionl.member)
        variable_alias.set_object(obj)
    elif expression.expressionl.quelifier == 4:
        pass


# +++++++++++++++++ General +++++++++++++++++