from colony.node import Colony, Node, MappingArgInputPort
from colony.observer import Observer


class RememberingObserver(Observer):

    def __init__(self):
        super(RememberingObserver, self).__init__()
        self.calls = []

    def notify(self, event):
        self.calls.append(event)


def target(x):
    return 2*x

if __name__ == '__main__':

    obs = RememberingObserver()
    col = Colony()

    map_node = col.add(Node,
        target=target,
        reactive_input_ports=MappingArgInputPort())
    map_node.output_port.register_observer(obs)

    map_node.reactive_input_ports[0].notify([1, 2, 3])
    map_node.reactive_input_ports[0].notify([3, 4, 5])

    print(obs.calls)