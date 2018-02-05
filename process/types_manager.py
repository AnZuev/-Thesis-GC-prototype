from process.ds import *
from javalang.javalang.tree import *


class TypesManager:
    instance = None

    def __init__(self):
        # stores class
        self.types = dict()

    @staticmethod
    def get():
        return TypesManager.instance

    def get_class_info(self, name):
        result_class = self.types.get(name, None)
        if not result_class:
            raise Exception("TypesManager: no class with name {}".format(name))
        return result_class

    def add_class_info(self, class_info):
        self.types[class_info.name] = class_info

    def determine_type(self, qualifier, method_info):
        # for method invocations like this.a
        # qualifier equals to None
        # !! could be buggy
        # wrong logic, has to be rewritten
        #
        if not qualifier:
            return method_info.scope.this.name

        path = qualifier.split('.')
        result_type = method_info.get_type_of_local_variable(path[0])

        if not result_type:
            result_type = method_info.scope.this.get_type_of_the_field(path[0])

        for sub_path in path[1:]:
            next_class_info = self.get_class_info(result_type)
            if not next_class_info:
                raise Exception("There is no class {}"
                                .format(result_type))
            next_result_type = next_class_info.get_type_of_the_field(sub_path)
            if not next_result_type:
                raise Exception("There is no filed {} in class {}"
                                .format(sub_path, result_type))
            result_type = next_result_type
        return result_type


def init_types_manager(tree):
    types_manager = TypesManager()
    # getting all nodes that represent classes
    class_nodes = map(lambda item: item[1], tree.filter(ClassDeclaration))
    for class_node in class_nodes:
        class_info = ClassInfo(class_node)
        types_manager.add_class_info(class_info)
    TypesManager.instance = types_manager


