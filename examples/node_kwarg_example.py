from colony.node import Graph, Node, MappingArgInputPort
from colony.observer import Observer


class RememberingObserver(Observer):

    def __init__(self):
        super(RememberingObserver, self).__init__()
        self.calls = []

    def notify(self, event):
        self.calls.append(event)


def _pow(x, a=1):
    return x**a

if __name__ == '__main__':

    obs = RememberingObserver()
    col = Graph()

    node = col.add(Node,
        target=_pow,
    )

    node.output_port.register_observer(obs)

    node.reactive_input_ports[0].notify(1)
    node.reactive_input_ports[0].notify(2)
    node.reactive_input_ports[0].notify(3)

    node.passive_input_ports['a'].notify(2)

    node.reactive_input_ports[0].notify(1)
    node.reactive_input_ports[0].notify(2)
    node.reactive_input_ports[0].notify(3)

    print(obs.calls)