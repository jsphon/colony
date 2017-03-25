from colony.node import Colony, Node, NodeEvent
from colony.observer import Observer


class RememberingObserver(Observer):

    def __init__(self):
        super(RememberingObserver, self).__init__()
        self.calls = []

    def notify(self, event):
        self.calls.append(event.payload)


def _x_squared(x):
    return x*x


if __name__ == '__main__':

    obs = RememberingObserver()
    col = Colony()

    node = col.add(Node, target=_x_squared)
    node.output_port.register_observer(obs)

    node.input_port.notify(NodeEvent(1))
    node.input_port.notify(NodeEvent(2))
    node.input_port.notify(NodeEvent(3))

    print(obs.calls)
