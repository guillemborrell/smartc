from uuid import uuid4


def gen_short_random():
    return '_' + str(uuid4())[:8]

class Attribute:
    def __init__(self, name, type):
        self.name = name
        self.type = type
        self.value = None


class State:
    def __init__(self, name, graph):
        self.name = name
        self.graph = graph
        self.value = None

        
class Method:
    def __init__(self, f):
        self.name = f.__name__
        self.function = f
        self.graph = None

    def __call__(self, *args):
        ev_name = self.name + gen_short_random()

        is_attribute = [type(a) == Attribute for a in args]

        if all(is_attribute):
            self.graph = {}
            for arg in args:
                if type(arg) != Attribute:
                    raise ValueError(
                        'All the arguments of the first step'
                        ' have to be attributes'
                        )
                self.graph[arg.name] = None
            
        else:
            self.graph = args[0].graph
            for arg in args:
                if type(arg) == State:
                    if self.graph:
                        self.graph.update(arg.graph)
                elif type(arg) == Attribute:
                    self.graph[arg.name] = None
                else:
                    raise ValueError(
                        'Method arguments can only be of State'
                        ' or Attribute type'
                        )

        self.graph[ev_name] = (self.function, tuple(a.name for a in args))
        return State(ev_name, self.graph)

        
def node(f):
    return Method(f)
            
if __name__ == '__main__':
    @node
    def something(a):
        return 2*a

    @node
    def another(x,y):
        return x+y
    
    a = Attribute('a', float)
    b = something(a)
    c = something(b)

    y = another(b, c)
    
    print(y.graph)
