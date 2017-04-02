from colony.node import Graph, Node
from colony.observer import RememberingObserver


def x_squared(x):
    return x * x


def x_plus_one(x):
    return x+1


if __name__ == '__main__':

    obs = RememberingObserver()
    col = Graph()

    node1 = col.add(Node, target=x_squared)
    node2 = col.add(Node, target=x_plus_one, node_args=node1)

    node2.output_port.register_observer(obs)

    node1.reactive_input_ports[0].notify(1)
    node1.reactive_input_ports[0].notify(2)
    node1.reactive_input_ports[0].notify(3)

    print(obs.calls)
