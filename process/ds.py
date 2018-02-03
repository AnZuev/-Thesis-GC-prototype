from enum import Enum
from javalang.javalang.tree import LocalVariableDeclaration


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
            method_info = MethodInfo(method)
            scope = Scope(self)
            method_info.attach_scope(scope)
            self.add_method(method_info)


class MethodInfo:
    def __init__(self, method_obj):
        self.title = method_obj.name
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
            print("There is no param", param_name, "in method", self.title)

    def get_gc(self, param_name):
        return self.input_param_table[param_name]

    def attach_scope(self, scope):
        self.scope = scope

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

    # returns type of the local variable if there is variable with such name
    # otherwise return None
    def get_type_of_local_variable(self, var_name):
        return self.local_variables.get(var_name, None)


class Scope:
    def __init__(self, this, parent=None):
        self.local_variables = dict()
        self.parent = parent
        self.this = this

    def add_local_variable(self, var):
        self.local_variables[var.name] = var

    def get_local_variable(self, var_name):
        variable = self.local_variables.get(var_name, None)
        if variable:
            return variable
        elif self.parent:
            return self.parent.get_local_variable(var_name)
        else:
            return None

    def get_parent(self):
        return self.parent


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

    def __init__(self):
        self.ref_counter = 0
        self.id = Object._id
        self.refers = []
        Object._id += 1

    def add_refer(self, obj):
        self.refers.append(obj)

    def remove_refer(self, obj):
        self.refers = filter(lambda o: o != obj, self.refers)

    def ref(self):
        self.ref_counter += 1

    def unref(self):
        self.ref_counter -= 1
        if self.ref_counter < 0:
            raise Exception("Somehow ref counter is less than 0")
        elif self.ref_counter == 0:
            print("Object with id {} could be deleted".format(self.id))


class Heap:
    def __init__(self):
        self.pool = set([])

    def collect_garbage(self):
        without_garbage = list(filter(lambda x: x.ref_counter > 0, self.pool))
        print("{} objects could be erased".format(len(Heap.pool) - len(without_garbage)))
        Heap.pool = without_garbage

    def allocate_object(self):
        obj = Object()
        self.pool.add(obj)
        return obj

    def print(self):
        for obj in self.pool:
            print("id = {}, ref_counter = {}".format(obj.id, obj.ref_counter))


