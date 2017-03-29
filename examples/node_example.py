from colony.node import Colony, Node
from colony.observer import RememberingObserver


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
