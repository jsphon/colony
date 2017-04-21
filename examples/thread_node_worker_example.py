from colony.node import Graph, Node, AsyncNodeWorker
from colony.observer import RememberingObserver
import time

def _x_squared(x):
    return x * x


if __name__ == '__main__':

    obs = RememberingObserver()
    col = Graph()

    node = col.add(Node,
                   node_worker_class=AsyncNodeWorker,
                   target_func=_x_squared,)
    node.output_port.register_observer(obs)

    # Long way to notify an input port
    node.reactive_input_ports[0].notify(1)
    node.reactive_input_ports[0].notify(2)
    node.reactive_input_ports[0].notify(3)

    print(obs.calls)

    # Short way to notify an input port
    obs.calls.clear()
    node.notify(4)
    node.notify(5)
    node.notify(6)

    time.sleep(0.1)
    print(obs.calls)

    print('Node value is %s'%node.get_value())