from colony.node import Colony, Node, NodeEvent
from colony.observer import Observer


class RememberingObserver(Observer):
    def __init__(self):
        super(RememberingObserver, self).__init__()
        self.calls = []

    def notify(self, event):
        self.calls.append(event.payload)


def _x_squared(x):
    return x * x


if __name__ == '__main__':
    obs = RememberingObserver()
    col = Colony()

    node = col.add(Node,
                   target=_x_squared,)
    node.output_port.register_observer(obs)

    node.reactive_input_ports[0].notify(1)
    node.reactive_input_ports[0].notify(2)
    node.reactive_input_ports[0].notify(3)

    print(obs.calls)
