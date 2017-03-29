from multiprocessing import Process

from colony.node import Colony, AsyncNode
from colony.observer import ProcessSafeRememberingObserver


def x_squared(x):
    return x * x


if __name__ == '__main__':
    obs = ProcessSafeRememberingObserver()
    col = Colony()

    node = col.add(AsyncNode,
                   target=x_squared,
                   async_class=Process)
    node.output_port.register_observer(obs)

    col.start()

    node.reactive_input_ports[0].notify(1)
    node.reactive_input_ports[0].notify(2)
    node.reactive_input_ports[0].notify(3)

    col.kill()
    obs.kill()

    print(obs.calls)
