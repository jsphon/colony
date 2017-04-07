from colony.node import Graph, Node
from colony.observer import RememberingObserver


def x_squared(x):
    return x * x


def x_plus_a(x, a=0):
    return x+a


if __name__ == '__main__':

    obs = RememberingObserver()
    col = Graph()

    node1 = col.add(Node, target_func=x_squared)
    node2 = col.add(Node, target_func=x_plus_a, node_kwargs={'a':node1})

    node2.output_port.register_observer(obs)

    node1.notify(1)
    node1.notify(2)
    node1.notify(3)

    node2.notify(1)
    node2.notify(2)
    node2.notify(3)

    print(obs.calls)
