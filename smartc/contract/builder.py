from uuid import uuid4
from collections import namedtuple
from graphviz import Digraph


def gen_short_random():
    return '_' + str(uuid4())[:8]


class Attribute:
    def __init__(self, name, attr_type,
                 mutable=False, multiple=False, allowed=None):
        self.name = name
        self.attr_type = attr_type
        self.value = None
        self.mutable = mutable
        self.multiple = multiple
        if type(allowed) == list:
            self.allowed = allowed
        elif type(allowed) == tuple:
            self.allowed = list(allowed)
        else:
            self.allowed = [allowed]

class GraphNode:
    def __init__(self, args, method, value):
        self.args = args
        self.method = method
        self.value = value
        self.to = []

    def add_target(self, target):
        self.to.append(target)

    def __repr__(self):
        return '[{}]'.format(', '.join(self.to))
        

class Node:
    def __init__(self, name, graph, attrs=None):
        self.name = name
        self.graph = graph
        self.value = None
        self.attrs = {}

        if attrs:
            self.attrs.update(attrs)

        
class Method:
    def __init__(self, f):
        self.name = f.__name__
        self.function = f
        self.graph = None
        self.attrs = {}

    def __call__(self, *args):
        ev_name = self.name + gen_short_random()
        is_attribute = [type(a) == Attribute for a in args]
        self.graph = {}

        if all(is_attribute):
            for arg in args:
                if type(arg) != Attribute:
                    raise ValueError(
                        'All the arguments of the first step'
                        ' have to be of type Attributes'
                        )
                self.graph[arg.name] = GraphNode(None, None, None)
                self.attrs[arg.name] = arg
        else:
            for arg in args:
                if type(arg) == Node:
                    self.graph.update(arg.graph)
                    self.attrs.update(arg.attrs)
                elif type(arg) == Attribute:
                    if arg.name not in self.graph:
                        self.graph[arg.name] = GraphNode(None, None, None)
                    self.attrs[arg.name] = arg
                else:
                    raise ValueError(
                        'Method arguments can only be of Node'
                        ' or Attribute type'
                        )

        self.graph[ev_name] = GraphNode(tuple(a.name for a in args),
                                        self.function,
                                        None)
        for arg in args:
            self.graph[arg.name].add_target(ev_name)
            
        return Node(ev_name, self.graph, attrs=self.attrs)

        
def node(f):
    return Method(f)


def visualize(node):
    dot = Digraph(comment='Contract graph', format='png')
    for k in node.graph:
        dot.node(k, k)
        
    for k, v in node.graph.items():
        if v.args is not None:
            for arg in v.args:
                dot.edge(arg, k, v.method.__name__)
        
    dot.render()
            

class Contract:
    def __init__(self, node=None):
        self.graph = None
        self.attrs = None
        if node:
            self.graph = node.graph
            self.attrs = node.attrs

    @classmethod
    def from_graph(cls, graph, attrs):
        cls.graph = tree
        cls.attrs = attrs

        return cls

    def visualize(self):
        dot = Digraph(comment='Contract graph', format='png')
        for k, v in self.graph.items():
            if v.value is not None:
                dot.node(k, k, color='blue')
            else:
                dot.node(k, k)
        
        for k, v in self.graph.items():
            if v.args is not None:
                for arg in v.args:
                    dot.edge(arg, k, v.method.__name__)
        
        dot.render()

    def _leaf_eval(self, key):
        targets = self.graph[key].to
        for target in targets:
            args = self.graph[target].args
            condition = [self.graph[a].value is not None for a in args]
            if all(condition):
                eval_args = [self.graph[a].value for a in args]
                print('Eval {} with args {}'.format(
                    self.graph[target].method.__name__,
                    eval_args
                )
                      )
                self.graph[target].value = self.graph[target].method(*eval_args)
                for k in self.graph[key].to:
                    yield self._leaf_eval(k)
        
    def set(self, attribute, value):
        if attribute in self.attrs:
            if type(value) == self.attrs[attribute].attr_type:
                self.graph[attribute].value = value
                print('Trying to evaluate...')
                for key in self._leaf_eval(attribute):
                    pass

            else:
                raise ValueError(
                    'Attribute {} not of type {}'.format(
                        attribute, self.attrs[attribute].attr_type)
                )
        else:
            raise ValueError(
                'Attribute {} not present in the graph'.format(
                    attribute
                    )
                )

        
if __name__ == '__main__':
    @node
    def something(a):
        return 2*a

    @node
    def another(x,y):
        return x+y
    
    a = Attribute('a', float)
    b = Attribute('b', int)
    c = something(a)

    x = another(a, c)
    y = another(b, x)
    
    contract = Contract(y)
    contract.set('a', 1.0)
    contract.set('b', 2)
    contract.visualize()

    
