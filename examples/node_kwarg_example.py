from colony.node import Graph, Node
from colony.observer import RememberingObserver


def _pow(x, a=1):
    return x**a


if __name__ == '__main__':

    obs = RememberingObserver()
    col = Graph()

    node = col.add(Node, target_func=_pow)

    node.output_port.register_observer(obs)

    node.notify(1)
    node.notify(2)
    node.notify(3)

    node.passive_input_ports['a'].notify(2)

    node.notify(1)
    node.notify(2)
    node.notify(3)

    print(obs.calls)