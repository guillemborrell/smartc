#   Smartc. Smart contracts for real time applications.
#   Copyright (C) 2017 Guillem Borrell i Nogueras (@guillemborrell)
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published
#   by the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

from uuid import uuid4
# You need python-graphviz and graphviz, the system library.
from graphviz import Digraph


def gen_short_random():
    """
    Convenience function that creates an 8-character random string
    """
    return '_' + str(uuid4())[:8]


class Attribute:
    """
    Attribute class, that is mostly used as a struct. Attributes are
    listed within a contract, and they may have different properties
    that act on their behavior. The three key attributes are *name*,
    *attr_type* and *value*, which are the name of the attribute,
    the type of the value and the value respectively. They are mandatory.

    The other attributes are to support how the contract works in
    practice. An attribute is mutable if can be modified after it has
    been set. It is multiple if it is a list, and values can be appended
    to it. The *allowed* attribute is used to implement access control,
    since some attributes can be only manipulated from users with granted
    permission. Finally, a variable is blocked if no user can set its value
    until some function of the contract changes this flag.
    """
    def __init__(self, name, attr_type,
                 mutable=False, multiple=False,
                 allowed=None, blocked=False):
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
    """
    Class with the information that each node must store. It is instantiated
    by the Method class, so you probably never have to use it.

    A node evaluates a function from some attributes once all the attributes
    are available. It also stores the target nodes to be able to follow the
    graph to the depending nodes.

    :param args: Arguments of the function to be evaluated
    :param method: Function to be evaluated
    :param value: Result of the function
    """
    def __init__(self, args, method, value, min_args=None, post_eval=None):
        self.args = args
        self.method = method
        self.value = value
        self.min_args = min_args
        self.post_eval = post_eval 
        self.to = []

    def add_target(self, target):
        """
        Appends a target node to this node
        """
        self.to.append(target)

    def __repr__(self):
        """
        The text representation is the targets and the value
        """
        return '[{}] : {}'.format(', '.join(self.to), self.value)


class Node:
    """
    Convenience class to build the contract. It stores all the
    necessary information from the graph as it is built, and it is
    returned by the @node decorator (see below).
    """
    def __init__(self, name, graph, attrs=None):
        self.name = name
        self.graph = graph
        self.value = None
        self.attrs = {}

        if attrs:
            self.attrs.update(attrs)


class Method:
    """
    Fundamental class to build the graph programatically. The @node
    decorator basically hides the initialization of this class. It
    builds the graph in a node from all the previous nodes.
    """
    def __init__(self, f):
        self.name = f.__name__
        self.function = f
        self.graph = None
        self.attrs = {}
        self.ev_name = None

    @staticmethod
    def _merge_graphs(graph1, graph2):
        """
        Convenience function to merge the graph coming from two nodes
        """
        keys_graph1 = [k for k in graph1]
        keys_graph2 = [k for k in graph2]
        keys_graph1.extend(keys_graph2)
        keys_set = set(keys_graph1)
        result = dict()

        for k in keys_set:
            if k in graph1 and k not in graph2:
                result[k] = graph1[k]

            elif k in graph2 and k not in graph1:
                result[k] = graph2[k]

            elif k in graph1 and k in graph2:
                targets = list(set(graph1[k].to + graph2[k].to))
                value = graph1[k]
                value.to = targets                    
                result[k] = value
                
        return result

    def __call__(self, *args):
        """
        This is what makes the trick of delayed evaluation. Calling the
        object does not actually compute anything, it builds the graph
        from the dependencies, that can be either arguments or nodes.
        """
        # This is the name of the node, that comes from the name of the
        # name of the function that is evaluated
        self.ev_name = self.name + gen_short_random()

        # Empty graph, that will be build from the preceding nodes
        self.graph = {}

        for arg in args:
            if type(arg) == Node:
                # If the arguments are nodes, merge the different graphs
                self.graph = self._merge_graphs(self.graph, arg.graph)
                self.attrs.update(arg.attrs)
            elif type(arg) == Attribute:
                # If the argument is an attribute, update the graph and
                # the list of arguments
                if arg.name not in self.graph:
                    self.graph[arg.name] = GraphNode((), None, None)
                self.attrs[arg.name] = arg
            else:
                raise ValueError(
                    'Method arguments can only be of Node'
                    ' or Attribute type'
                    )

        # Update the graph with the present node
        self.graph[self.ev_name] = GraphNode(tuple(a.name for a in args),
                                        self.function,
                                        None)

        # Update the list of targets in the preceding nodes
        for arg in args:
            self.graph[arg.name].add_target(self.ev_name)

        # Return a node to keep building.
        return Node(self.ev_name, self.graph, attrs=self.attrs)


def gather(*args, condition=None):
    def _gather_function(*args):
        for a in args:
            if a is not None:
                return a

    method = Method(_gather_function)
    node = method(*args)
    node.graph[method.ev_name].min_args = 1
    if condition is None:
        node.graph[method.ev_name].post_eval = all

    return node


def node(f):
    """
    Decorator that is used to build a task graph with delayed evaluation.
    It decorates functions that depend on arguments of class Attribute
    or Node.

    >>> from smartc.contract.builder import node
    >>> from smartc.contract.builder import Attribute
    >>> @node
    ... def timestwo(a):
    ...     return 2*a
    >>> @node
    ... def add(x, y):
    ...     return x + y
    >>> a = Attribute('a', float)
    >>> b = Attribute('b', float)
    >>> c = timestwo(a)
    >>> d = add(b, c)
    >>> print(d.graph)
    {'b': [add_2787ddee: None], 'a': [timestwo_100ec180: None], 'timestwo_100ec180': [add_2787ddee: None], 'add_2787ddee': [: None]}
    """
    return Method(f)


def visualize(node):
    """
    Visualize the graph at a given node with graphviz.
    """
    dot = Digraph(comment='Contract graph', format='png')
    for k in node.graph:
        dot.node(k, k)

    for k, v in node.graph.items():
        if v.args is not None:
            for arg in v.args:
                dot.edge(arg, k, v.method.__name__)

    dot.render()


class Contract:
    """
    Class that builds and evaluates a contract given a node in
    the task graph.

    :param node:  Node of type Node, usually the last node in the task graph
    """
    @staticmethod
    def _build_eval_graph(graph):
        """
        Convenience function that updates the eval graph. The contract
        stores an additional graph that is used to check when a node has
        to be evaluated, the eval_graph. It basically stores a dict with
        two keys, 'total' is the number of preceding nodes, and 'eval' 
        is set to 1 or True if the node can be evaluated.
        """
        eval_graph = {}
        for k, v in graph.items():
            if v.min_args is None:
                eval_graph[k] = dict(total=len(v.args), eval=0)
            else:
                eval_graph[k] = dict(total=v.min_args, eval=0)

        return eval_graph

    def __init__(self, node=None):
        """
        Class initialization. In addition to store the graph and the
        attributes, it also creates the evaluation graph and the list
        of attributes that have been previously used for delayed evaluation.
        """
        self.graph = None
        self.attrs = None
        if node:
            self.graph = node.graph
            self.attrs = node.attrs

        self.eval_graph = self._build_eval_graph(node.graph)
        self.applied_attributes = []
        self.post_eval_dict = {}

    def visualize(self):
        """
        Visualize the contract graph. It is equivalent to visualize
        the node that was used to build the contract.
        """
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
        """
        Generator that traverses the graph fetching all the nodes.
        """
        for target in self.graph[node].to:
            yield target
            for subtarget in self.graph[target].to:
                for t in self._traverse(subtarget):
                    yield t

    def _next_node_to_eval(self, attribute):
        """
        This function returns the next node that has to be evaluated
        within the grap. When all the previous nodes have been evaluated,
        it returns the node and resets the graph walk.
        """
        self.eval_graph[attribute]['eval'] = 1
        for node in self._traverse(attribute):
            # Check the number of previous evaluations
            previous = self.graph[node].args
            evals = sum([self.eval_graph[n]['eval'] for n in previous])
            has_value = self.eval_graph[node]['eval']
            if evals >= self.eval_graph[node]['total'] and not has_value:
                return node

    def _node_eval(self, attribute):
        """
        Starting from the given attribute, evaluate all the nodes that
        can be evaluated (see _next_node_to_eval). 
        """
        for i in range(len(self.eval_graph) + 1):  # I know max evals
            print('Graph walk', i+1)
            key = self._next_node_to_eval(attribute)
            if key:
                args = self.graph[key].args
                eval_args = [self.graph[a].value for a in args]
                print('Eval {} in node {} with args {}'.format(
                    self.graph[key].method.__name__,
                    key,
                    eval_args))
                value = self.graph[key].method(*eval_args)
                self.graph[key].value = value
                print('Set', key, 'with value', value)

                self.eval_graph[key]['eval'] = 1

                if self.graph[key].post_eval:
                    print("Setting for post evaluation")
                    self.post_eval_dict[key] = (self.graph[key].method, eval_args)
            else:
                break

    def set(self, attribute, value):
        """
        Set an attribute and trigger delayed evaluation of the task graph.

        :param attribute: Name of the attribute to be evaluated.
        :param value: Value of the attribute with a correct type.
        """
        print('Set attribute', attribute)
        if attribute in self.attrs:
            if type(value) == self.attrs[attribute].attr_type:

                # Execute post evaluations
                for k, v in self.post_eval_dict.items():
                    condition = v[0](*v[1])
                    if not condition:
                        print("--------> Changing evaluation switch")
                        self.graph[key].eval = 0
                        
                self.graph[attribute].value = value
                print('Walk from', attribute)
                self._node_eval(attribute)
                # Traverse from the other attributes in case there are
                # additional paths
                for other_attribute in self.applied_attributes:
                    print('Walk from', other_attribute)
                    self._node_eval(other_attribute)

                self.applied_attributes.append(attribute)

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

    def run(self, **attributes):
        """
        Run a contract setting multiple attributes as keyword arguments.
        """
        for k, v in attributes.items():
            self.set(k, v)

    def append(self, attribute, value):
        """
        Appends an item to a present multiple attribute.
        """
        pass


if __name__ == '__main__':
    @node
    def something(a):
        return 2*a

    @node
    def another(x, y):
        return x + y

    @node
    def result(z):
        print('The final result is {}'.format(z))
        return z

    a = Attribute('a', float)
    b = Attribute('b', int)
    c = something(a)
    x = another(a, c)
    q = something(a)
    y = another(b, x)
    z = another(y, q)

    contract = Contract(z)
    contract.set('a', 1.0)
    contract.set('b', 2)

    contract.visualize()
