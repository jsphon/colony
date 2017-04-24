from colony.node import AsyncNode, MappingArgInputPort
from colony.observer import ProcessSafeRememberingObserver


def target(x):
    return 2 * x


if __name__ == '__main__':
    obs = ProcessSafeRememberingObserver()

    map_node = AsyncNode(target_func=target,
                         reactive_input_ports=MappingArgInputPort())
    map_node.start()
    map_node.output_port.register_observer(obs)

    map_node.notify([1, 2, 3])
    map_node.notify([3, 4, 5])

    map_node.worker.stop()
    obs.stop()

    print('observer called with:')
    print(obs.calls)

    expected = set([2, 4, 6, 6, 8, 10])
    assert expected == obs.call_set
