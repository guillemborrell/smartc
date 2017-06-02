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
        return '[{}: {}]'.format(', '.join(self.to), self.value)
        

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
                self.graph[arg.name] = GraphNode((), None, None)
                self.attrs[arg.name] = arg
        else:
            for arg in args:
                if type(arg) == Node:
                    self.graph.update(arg.graph)
                    self.attrs.update(arg.attrs)
                elif type(arg) == Attribute:
                    if arg.name not in self.graph:
                        self.graph[arg.name] = GraphNode((), None, None)
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
    @staticmethod
    def _build_eval_graph(graph):
        eval_graph = {}
        for k, v in graph.items():
            eval_graph[k] = dict(total=len(v.args), eval=0)

        return eval_graph
    
    def __init__(self, node=None):
        self.graph = None
        self.attrs = None
        if node:
            self.graph = node.graph
            self.attrs = node.attrs

        self.eval_graph = self._build_eval_graph(node.graph)
        
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

    def _traverse(self, node):
        for target in self.graph[node].to:
            yield target
            for subtarget in self.graph[target].to:
                for t in self._traverse(subtarget):
                    yield t
        
    def _next_node_to_eval(self, attribute):
        self.eval_graph[attribute]['eval'] = 1
        for node in self._traverse(attribute):
            # Check the number of previous evaluations
            previous = self.graph[node].args
            evals = sum([self.eval_graph[n]['eval'] for n in previous])
            if evals == self.eval_graph[node]['total']:
                return node
        
    def _leaf_eval(self, key):
        for _ in range(10000):  # Max evals. Never use while.
            key = self._next_node_to_eval(key)
            if key:
                args = self.graph[key].args
                eval_args = [self.graph[a].value for a in args]
                print('Eval {} in node {} with args {}'.format(
                    self.graph[key].method.__name__,
                    key,
                    eval_args))
                self.graph[key].value = self.graph[key].method(*eval_args)
                self.eval_graph[key]['eval'] = 1
                
            else:
                break
        
    def set(self, attribute, value):
        if attribute in self.attrs:
            if type(value) == self.attrs[attribute].attr_type:
                self.graph[attribute].value = value
                self._leaf_eval(attribute)

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

    def run(self, attributes):
        for k, v in attributes.items():
            self.set(k, v)

    def append(self, attribute, value):
        pass

        
if __name__ == '__main__':
    @node
    def something(a):
        return 2*a

    @node
    def another(x,y):
        return x+y

    @node
    def result(z):
        print('The final result is {}'.format(z))
        return z
    
    a = Attribute('a', float)
    b = Attribute('b', int)
    c = something(a)

    x = another(a, c)
    y = another(b, x)
    z = result(y)
    
    contract = Contract(z)
    contract.set('a', 1.0)
    contract.set('b', 2)

    contract.visualize()

