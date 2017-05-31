from uuid import uuid4
from collections import namedtuple
from graphviz import Graph


GraphNode = namedtuple('GraphNode', ['args', 'method', 'value'])


def gen_short_random():
    return '_' + str(uuid4())[:8]

class Attribute:
    def __init__(self, name, type):
        self.name = name
        self.type = type
        self.value = None


class Node:
    def __init__(self, name, graph, attributes=()):
        self.name = name
        self.graph = graph
        self.value = None
        self.attributes = list(attributes)

        
class Method:
    def __init__(self, f):
        self.name = f.__name__
        self.function = f
        self.graph = None
        self.attributes = []

    def __call__(self, *args):
        ev_name = self.name + gen_short_random()
        is_attribute = [type(a) == Attribute for a in args]
        self.graph = {}

        if all(is_attribute):
            for arg in args:
                if type(arg) != Attribute:
                    raise ValueError(
                        'All the arguments of the first step'
                        ' have to be attributes'
                        )
                self.graph[arg.name] = GraphNode(None, None, None)
            
        else:
            for arg in args:
                if type(arg) == Node:
                    if self.graph:
                        self.graph.update(arg.graph)
                elif type(arg) == Attribute:
                    self.graph[arg.name] = GraphNode(None, None, None)
                else:
                    raise ValueError(
                        'Method arguments can only be of Node'
                        ' or Attribute type'
                        )

        self.graph[ev_name] = GraphNode(tuple(a.name for a in args),
                                        self.function,
                                        None)
        return Node(ev_name, self.graph)

        
def node(f):
    return Method(f)


def visualize(node):
    dot = Graph(comment='Contract graph', format='png')
    for k in node.graph:
        dot.node(k, k)
        
    for k, v in node.graph.items():
        if v.args is not None:
            for arg in v.args:
                dot.edge(k, arg, v.method.__name__)
        
    dot.render()
            

class Contract:
    def __init__(self, node):
        self.graph = node.graph

        
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
    d = something(b)

    x = another(a, c)
    y = another(b, x)
    
    visualize(y)
    
