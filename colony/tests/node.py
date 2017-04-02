import unittest
from multiprocessing import Process
from threading import Thread

from colony.node import AsyncNode
from colony.node import Graph, Node, MappingArgInputPort
from colony.observer import RememberingObserver, ProcessSafeRememberingObserver

EPS = 0.01


def _x_squared(x):
    return x * x


def _x_plus_one(x):
    return x + 1


class NodeTests(unittest.TestCase):
    def test_calls_observer(self):
        obs = RememberingObserver()
        col = Graph()

        node = col.add(Node,
                       target=_x_squared, )
        node.output_port.register_observer(obs)

        node.reactive_input_ports[0].notify(1)
        node.reactive_input_ports[0].notify(2)
        node.reactive_input_ports[0].notify(3)

        col.stop()

        print(obs.calls)

        self.assertEqual([1, 4, 9], obs.calls)


class AsyncNodeTests(unittest.TestCase):
    def test_kill(self):
        obs = ProcessSafeRememberingObserver()
        col = Graph()

        node = col.add(AsyncNode,
                       target=_x_squared,
                       async_class=Process)
        node.output_port.register_observer(obs)

        col.start()
        col.stop()
        obs.stop()

        self.assertEqual([], obs.calls)

    def test_calls_observer_process(self):
        for async_class in (Thread, Process):
            self.do_test_calls_observer_process(async_class)

    def do_test_calls_observer_process(self, async_ckass):
        obs = ProcessSafeRememberingObserver()
        col = Graph()

        node = col.add(AsyncNode,
                       target=_x_squared,
                       async_class=async_ckass,
                       num_threads=1)
        node.output_port.register_observer(obs)

        col.start()

        node.reactive_input_ports[0].notify(1)
        node.reactive_input_ports[0].notify(2)
        node.reactive_input_ports[0].notify(3)

        col.stop()
        obs.stop()

        self.assertEqual([1, 4, 9], obs.calls)

    def test_map(self):
        for async_class in (Thread, Process,):
            self.do_test_map(async_class)

    def do_test_map(self, async_class):

        obs = ProcessSafeRememberingObserver()
        graph = Graph()

        map_node = graph.add(AsyncNode,
                             target=_x_squared,
                             async_class=async_class,
                             reactive_input_ports=MappingArgInputPort())
        map_node.output_port.register_observer(obs)

        graph.start()

        map_node.reactive_input_ports[0].notify([1, 2, 3])
        map_node.reactive_input_ports[0].notify([3, 4, 5])

        graph.stop()
        obs.stop()

        expected = set([1, 4, 9, 9, 16, 25])
        actual = set(obs.calls)
        self.assertEqual(expected, actual)

    def test_arg(self):

        obs = RememberingObserver()
        col = Graph()

        node1 = col.add(Node, target=_x_squared)
        node2 = col.add(Node, target=_x_plus_one, node_args=node1)

        node2.output_port.register_observer(obs)

        node1.reactive_input_ports[0].notify(1)
        node1.reactive_input_ports[0].notify(2)
        node1.reactive_input_ports[0].notify(3)

        self.assertEqual({2, 5, 10}, obs.call_set)

# class AsyncNodeTests(unittest.TestCase):
#
#     def test_execute(self):
#         for async_class in (Thread, Process):
#             print('=== Executing test with async_class=%s ==='%async_class)
#             self.do_test_execute(async_class)
#
#     def do_test_execute(self, async_class):
#
#         observer = MagicMock()
#         n = AsyncNode(target=basic_target, async_class=async_class)
#         n.output_port.register_observer(observer)
#
#         child = AsyncNode(target=thread_target, async_class=Thread)
#         n.output_port.register_observer(child.input_port)
#
#         time.sleep(EPS)
#
#         # TEST
#         n.execute(NodeEvent('payload'))
#
#         # VERIFY
#         time.sleep(EPS)
#
#         self.assertEqual('thread_target(result payload)', child.get_value())
#
#         #self.assertEqual(1, observer.notify.call_count)
#         #self.assertEqual('result payload', observer.notify.call_args[0][0].payload)
#
#         # Tear Down
#         print('Killing')
#         n.kill()
#
#     def test_get_value(self):
#         for async_class in (Thread, Process):
#             self.do_test_get_value(async_class)
#
#     def do_test_get_value(self, async_class):
#
#         n = AsyncNode(target=basic_target, async_class=async_class)
#         # TEST
#         n.execute(NodeEvent('payload'))
#
#         # VERIFY
#         time.sleep(EPS)
#         self.assertEqual('result payload', n.get_value())
#
#         n.kill()
#
#
# class AsyncNodeWithArgTests(unittest.TestCase):
#
#     def test_execute(self):
#         for async_class in (Thread, Process):
#             self.do_test_execute(async_class)
#
#     def do_test_execute(self, async_class):
#         node_arg = AsyncNode(target=basic_target, async_class=async_class)
#
#         observer = MagicMock()
#         n = AsyncNode(target=target_with_arg, async_class=async_class, args=[node_arg])
#         n.output_port.register_observer(observer)
#
#         # TEST
#         n.execute(NodeEvent('data'))
#
#         # VERIFY
#         time.sleep(0.1)
#
#         self.assertEqual(1, observer.notify.call_count)
#         self.assertEqual(('data', None), observer.notify.call_args[0][0].payload)
#
#         node_arg.execute(NodeEvent('node arg test'))
#         time.sleep(EPS)
#         n.execute(NodeEvent('data2'))
#         time.sleep(EPS)
#
#         self.assertEqual(2, observer.notify.call_count)
#         self.assertEqual(('data2', 'result node arg test'), observer.notify.call_args[0][0].payload)
#
#         n.kill()
#         node_arg.kill()
#
#
# class AsyncNodeWithKwargTests(unittest.TestCase):
#     def test_execute_multi(self):
#         for async_class in (Thread, Process):
#             self.do_test_execute(async_class)
#
#     def do_test_execute(self, async_class):
#         node_kwarg = AsyncNode(target=basic_target, async_class=async_class)
#
#         observer = MagicMock()
#         n = AsyncNode(target=target_with_kwarg, kwargs={'kwarg1': node_kwarg})
#         n.output_port.register_observer(observer)
#
#         # TEST
#         n.execute(NodeEvent('data'))
#
#         # VERIFY
#         time.sleep(0.1)
#
#         self.assertEqual(1, observer.notify.call_count)
#         self.assertEqual(('data', None), observer.notify.call_args[0][0].payload)
#
#         node_kwarg.execute(NodeEvent('node kwarg test'))
#         time.sleep(EPS)
#         n.execute(NodeEvent('data2'))
#         time.sleep(EPS)
#
#         self.assertEqual(2, observer.notify.call_count)
#         self.assertEqual(('data2', 'result node kwarg test'), observer.notify.call_args[0][0].payload)
#
#         node_kwarg.kill()
#         n.kill()
#
#
# class BatchNodeInputTests(unittest.TestCase):
#     def test_notify(self):
#         for async_class in (Thread, Process):
#             self.do_test_notify(async_class=async_class)
#
#     def do_test_notify(self, async_class):
#         observer = MagicMock()
#         n = AsyncNode(target=basic_target, input_port=BatchNodeInput(2), async_class=async_class)
#         n.output_port.register_observer(observer)
#
#         # TEST
#         n.input_port.notify([1, 2, 3, 4])
#
#         # VERIFY
#         time.sleep(EPS)
#
#         self.assertEqual(2, observer.notify.call_count)
#         self.assertEqual('result [1, 2]', observer.notify.call_args_list[0][0][0].payload)
#         self.assertEqual('result [3, 4]', observer.notify.call_args_list[1][0][0].payload)
#
#         n.kill()
#
#
# class ListNodeInputTests(unittest.TestCase):
#     def test_notify(self):
#         for async_class in (Thread, Process):
#             self.do_test_notify(async_class)
#
#     def do_test_notify(self, async_class):
#         # SETUP
#         observer = MagicMock()
#         n = AsyncNode(target=basic_target, input_port=ListNodeInput(), async_class=async_class)
#         n.output_port.register_observer(observer)
#
#         # TEST
#         n.input_port.notify([1, 2, 3, 4])
#
#         # VERIFY
#         time.sleep(EPS)
#
#         self.assertEqual(4, observer.notify.call_count)
#         self.assertEqual('result 1', observer.notify.call_args_list[0][0][0].payload)
#         self.assertEqual('result 2', observer.notify.call_args_list[1][0][0].payload)
#         self.assertEqual('result 3', observer.notify.call_args_list[2][0][0].payload)
#         self.assertEqual('result 4', observer.notify.call_args_list[3][0][0].payload)
#
#         n.kill()


if __name__ == '__main__':
    unittest.main()
