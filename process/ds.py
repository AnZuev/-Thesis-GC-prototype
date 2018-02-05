from enum import Enum
from javalang.javalang.tree import LocalVariableDeclaration
from collections import Counter


# ArgGC - property of argument that passed to the method
# not_sure - can't say anything about such argument
# does_change - method affects the argument gc state
# does_not_change - method doesn't affect gc state of the passed object
class ArgGC(Enum):
    not_sure = 0,
    pass_forward = -1
    does_not_change = 1
    does_change = 2


class ClassInfo:
    def __init__(self, class_obj, parent=None):
        self.name = class_obj.name
        # name -> methodInfo
        self.methods = dict()
        self.constructors = []
        self.parent = parent
        # name -> type
        self.fields = dict()
        self.init_fields(class_obj.fields)
        self.init_methods(class_obj.methods)

    def get_method(self, name):
        return self.methods[name]

    def add_method(self, method):
        self.methods[method.title] = method

    def init_fields(self, fields):
        for field in fields:
            field_type = field.type.name
            for declarator in field.declarators:
                self.fields[declarator.name] = field_type

    def get_type_of_the_field(self, field):
        result_type = self.fields.get(field, None)
        # TODO: add searching in base classes, for now search for only in this class
        if not result_type:
            raise Exception("ClassInfo: There is no field"
                            " with name {} in class {}".format(self.title, field))
        return result_type

    def init_methods(self, methods):
        for method in methods:
            method_info = StandAloneMethodInfo(method)
            scope = Scope(self)
            method_info.attach_scope(scope)
            self.add_method(method_info)

    def init_constructors(self, constructors):
        for constructor in constructors:
            constructor_info = ClassConstructorInfo(constructor)
            scope = Scope(self)
            constructor_info.attach_scope(scope)
            self.constructors.append(constructor_info)


class MethodInfo:
    def __init__(self, method_obj):
        self.input_params = [(param.name, param.type.name) for param in method_obj.parameters]
        self.input_param_table = dict()
        self.scope = None
        self.method_obj = method_obj
        # name -> type
        self.local_variables = dict()
        self.init_local_variables()

        for name in self.input_params:
            self.input_param_table[name] = ArgGC.not_sure

    def change_gc(self, param_name, new_gc):
        if new_gc not in ArgGC:
            raise Exception("Couldn't assign", new_gc, "type to param", param_name)
        param = self.input_param_table.get(param_name, None)
        if param is not None:
            self.input_param_table[param_name] = new_gc
        else:
            print("There is no param", param_name, "in method")

    def get_gc(self, param_name):
        return self.input_param_table[param_name]

    def attach_scope(self, scope):
        self.scope = scope
        scope.set_method_info(self)

    def does_change_gc(self, var):
        return self.input_param_table[var]

    def init_local_variables(self):
        # adding passed params as local variables
        for param in self.method_obj.parameters:
            self.local_variables[param.name] = param.type.name

        # adding local variables itself
        local_var_declarations = map(lambda item: item[1], self.method_obj.filter(LocalVariableDeclaration))
        for declaration in local_var_declarations:
            var_type = declaration.type.name
            for declarator in declaration.declarators:
                self.local_variables[declarator.name] = var_type

    # returns type (static) of the local variable if there is variable with such name
    # otherwise return None
    def get_type_of_local_variable(self, var_name):
        return self.local_variables.get(var_name, None)


class StandAloneMethodInfo(MethodInfo):
    def __init__(self, method_obj):
        super().__init__(method_obj)
        self.title = method_obj.name


class ClassConstructorInfo(MethodInfo):
    def __init__(self, method_obj):
        super().__init__(method_obj)

    def get_fields_to_init(self):
        re




class VariableAlias:
    def __init__(self, name, obj=None, var_type=None):
        self.name = name
        self.type = var_type
        self.object = obj
        if self.object:
            self.object.ref()

    def set_object(self, obj):
        if self.object:
            self.object.unref()
        self.object = obj
        self.object.ref()

    def get_object(self):
        return self.object


class Object:
    _id = 1

    def __init__(self, heap):
        self.ref_counter = 0
        self.id = Object._id
        self.fields = dict()
        Object._id += 1
        self.heap = heap
        self.dynamic_type = None

    def set_field(self, field_name: str, obj: "Object"):
        self.fields[field_name] = obj
        obj.ref()

    def get_field_object(self, obj_path: list):
        if len(obj_path) == 0:
            return self
        if self.fields[obj_path[0]]:
            return self.get_field_object(obj_path[1:])

    def unset_field(self, field_name: str):
        self.fields[field_name].unref()
        self.fields[field_name] = None

    def ref(self):
        self.ref_counter += 1

    def unref(self):
        self.ref_counter -= 1
        if self.ref_counter < 0:
            raise Exception("Object:Somehow ref counter is less than 0")
        elif self.ref_counter == 0:
            print("Object with id {} could be deleted".format(self.id))
            self.heap.remove_object(self)

    def set_dynamic_type(self, dynamic_type: str):
        self.dynamic_type = dynamic_type


class Heap:
    def __init__(self):
        self.pool = set([])

    def collect_garbage(self):
        without_garbage = list(filter(lambda x: x.ref_counter > 0, self.pool))
        print("{} objects could be erased".format(len(Heap.pool) - len(without_garbage)))
        Heap.pool = without_garbage

    def allocate_object(self):
        obj = Object(self)
        self.pool.add(obj)
        return obj

    def print(self):
        for obj in self.pool:
            print("id = {}, ref_counter = {}".format(obj.id, obj.ref_counter))

    def remove_object(self, obj):
        for child_obj in obj:
            # remove chile objects
            pass
        self.pool.remove(obj)


class Scope:
    def __init__(self, this, parent=None):
        self.local_variables = dict()
        self.parent = parent
        self.this = this
        self.method_info = None

    def add_local_variable(self, var):
        self.local_variables[var.name] = var

    def get_local_variable(self, var_name) -> VariableAlias:
        variable = self.local_variables.get(var_name, None)
        if variable:
            return variable
        elif self.parent:
            return self.parent.get_local_variable(var_name)
        else:
            return None

    def remove_variables_from_the_scope(self):
        for var_name, var_alias in self.local_variables.items():
            # delete objects from the scope
            pass

    def get_parent(self):
        return self.parent

    def set_method_info(self, method_info):
        self.method_info = method_info

    def get_method_info(self):
        return self.method_info

