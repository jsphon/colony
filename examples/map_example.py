from colony.node import Graph, Node, MappingArgInputPort
from colony.observer import RememberingObserver


def target(x):
    return 2 * x


if __name__ == '__main__':
    obs = RememberingObserver()
    col = Graph()

    map_node = col.add(Node,
                       target=target,
                       reactive_input_ports=MappingArgInputPort())
    map_node.output_port.register_observer(obs)

    map_node.notify([1, 2, 3])
    map_node.notify([3, 4, 5])

    print(obs.calls)
