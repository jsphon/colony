from colony.node import Colony, Node
from colony.observer import RememberingObserver


def x_squared(x):
    return x * x


def x_plus_a(x, a=0):
    return x+a


if __name__ == '__main__':

    obs = RememberingObserver()
    col = Colony()

    node1 = col.add(Node, target=x_squared)
    node2 = col.add(Node, target=x_plus_a, node_kwargs={'a':node1})

    node2.output_port.register_observer(obs)

    node1.reactive_input_ports[0].notify(1)
    node1.reactive_input_ports[0].notify(2)
    node1.reactive_input_ports[0].notify(3)

    node2.reactive_input_ports[0].notify(1)
    node2.reactive_input_ports[0].notify(2)
    node2.reactive_input_ports[0].notify(3)

    print(obs.calls)
