from enum import Enum
from javalang.javalang.tree import MethodInvocation, ClassDeclaration
from process.types_manager import TypesManager


# Enum represents state of the FlowNode
# processed - the unit and everything before has been successfully processed
# ready - unit is able to be processed (all methods that this method depends on have been processed)
# not_ready - the unit is not able to be processed (there are not-yet-processed methods that this method depends on)
# is_being_processed - the unit is being processed
class FlowNodeState(Enum):
    ready = 1,
    not_ready = -1,
    is_being_processed = 0,
    processed = 2


# this class is used in order to represent a node (method)
# inside flow graph
# The graph is used to process methods in a way that
# any method that is being processed doesn't depend
# on not-yet processed method(s)
class FlowNode:
    # unit_id is actually "class_name"."method_name"
    def __init__(self, unit_id, class_ref, flow_graph):
        self.unit_id = unit_id
        self.before = set([])
        self.after = set([])
        self.class_ref = class_ref
        self.state = FlowNodeState.not_ready
        self.flow_graph = flow_graph
        self.wait_for = set([])

    def add_before(self, flow_node):
        self.before.add(flow_node)
        self.wait_for.add(flow_node)

    def add_after(self, flow_node):
        self.after.add(flow_node)

    def get_class_name(self):
        return self.unit_id.split('.')[0]

    def get_method_name(self):
        return self.unit_id.split('.')[1]

    def get_method_invocations(self):
        return map(lambda item: item[1], self.class_ref
                   .get_method(self.unit_id.split(".")[1])
                   .method_obj
                   .filter(MethodInvocation))

    def update(self, unit_id):
        if unit_id in self.wait_for:
            self.wait_for.remove(unit_id)
            self.refresh()

    def refresh(self):
        if len(self.wait_for) == 0:
            self.flow_graph.make_node_ready(self)


class FlowGraph:
    def __init__(self):
        # key - unit_id
        # value - unit to process
        self.flow_nodes = dict()

        # self.ready and self.not_ready stores unit_ids
        self.ready = set([])
        self.not_ready = set([])
        self.to_process = set([])

    def add_unit(self, class_name, method_name, unit=None):
        unit_id = class_name + "." + method_name
        if not self.flow_nodes.get(unit_id, None):
            flow_node = FlowNode(unit_id, unit, self)
            self.flow_nodes[unit_id] = flow_node
            self.not_ready.add(unit_id)

    def get_unit(self, unit_id):
        return self.flow_nodes.get(unit_id, None)

    def get_next_to_process(self):
        if len(self.to_process) > 0:
            return self.to_process.pop()

        self.get_stats()

    def get_stats(self):
        print("FlowGraph: no nodes to process:")
        print("---- len of 'to_process'{}".format(len(self.to_process)))
        print("---- len of 'ready'{}".format(len(self.ready)))
        print("---- len of 'not_ready'{}".format(len(self.not_ready)))
        print("---- len of 'flow_nodes'{}".format(len(self.flow_nodes)))
        print("-------------------\n")

    def get_ready_units(self):
        return self.ready

    def make_node_ready(self, node):
        node.state = FlowNodeState.ready
        self.not_ready.remove(node.unit_id)
        self.to_process.add(node.unit_id)

    def fill_methods_relations(self):
        print("Filling method relations:")
        for unit_id, node in self.flow_nodes.items():
            method_invocations = node.get_method_invocations()
            method_info = node.class_ref.get_method(node.get_method_name())
            print("   Processing '{}':".format(unit_id))
            for mi in method_invocations:
                # object which is being called
                qualifier = mi.qualifier
                # method name actually
                member = mi.member

                print("     -+- {}".format(member))
                object_type = TypesManager.get().determine_type(qualifier, method_info)
                print("      |___ type of called object '{}'".format(object_type))
                before_unit_id = ".".join([object_type, member])
                node.add_before(before_unit_id)
                self.get_unit(before_unit_id).add_after(unit_id)
            print("   '{}' finished\n".format(node.unit_id))

    def update_nodes_state(self):
        for unit_id, node in self.flow_nodes.items():
            node.refresh()


def init_raw_flow_graph(tree):
    flow_graph = FlowGraph()

    # getting all nodes that represent classes
    class_nodes = map(lambda item: item[1], tree.filter(ClassDeclaration))
    for class_node in class_nodes:
        for method in class_node.methods:
            flow_graph.add_unit(class_node.name, method.name, TypesManager.get().get_class_info(class_node.name))
    flow_graph.fill_methods_relations()
    flow_graph.update_nodes_state()
    return flow_graph

