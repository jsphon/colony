from colony.node import Node
from colony.observer import RememberingObserver


def x_squared(x):
    return x * x


def x_plus_one(x):
    return x+1


if __name__ == '__main__':

    obs = RememberingObserver()

    node1 = Node(target_func=x_squared)
    node2 = Node(target_func=x_plus_one, node_args=node1)

    node1.start()
    node2.start()

    node2.output_port.register_observer(obs)

    node1.notify(1)
    node1.notify(2)
    node1.notify(3)

    # Expect x**2 + 1 i.e. 2, 5, 10
    print(obs.calls)
