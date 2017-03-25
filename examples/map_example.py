from colony.node import Colony, MapNode, NodeEvent
from colony.observer import Observer


class RememberingObserver(Observer):

    def __init__(self):
        super(RememberingObserver, self).__init__()
        self.calls = []

    def notify(self, event):
        self.calls.append(event)


if __name__ == '__main__':

    obs = RememberingObserver()
    col = Colony()

    map_node = col.add(MapNode)
    map_node.output_port.register_observer(obs)

    map_node.input_port.notify(NodeEvent([1, 2, 3]))

    print(obs.calls)
