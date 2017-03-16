import unittest
from node_process import node
from node_process.node import AsyncNode, NodeEvent
from mock import MagicMock
import time
import multiprocessing
from threading import Thread
from multiprocessing import Process

EPS = 0.01


class AsyncNodeExample(node.AsyncNode):

    def do_work(self, payload):
        print('AsyncNodeExample doing work')
        return 'result %s'%payload


class AsyncNodeWithArgExample(node.AsyncNode):

    def do_work(self, payload, arg1):
        print('AsyncNodeWithArgExample(%s,%s)'%(payload, arg1))
        return payload, arg1


class AsyncNodeTests(unittest.TestCase):

    def setUp(self):
        self.observer = MagicMock()
        self.node = AsyncNodeExample()
        self.node.output.register_observer(self.observer)

    def tearDown(self):
        self.node.kill()

    def test_execute(self):

        # TEST
        self.node.execute(node.NodeEvent('payload'))

        # VERIFY
        time.sleep(EPS)

        self.assertEqual(1, self.observer.notify.call_count)
        self.assertEqual('result payload', self.observer.notify.call_args[0][0])

    def test_get_value(self):

        # TEST
        self.node.execute(node.NodeEvent('payload'))

        # VERIFY
        time.sleep(EPS)
        self.assertEqual('result payload', self.node.get_value())


class AsyncNodeWithArgTests(unittest.TestCase):

    def test_execute_multi(self):

        for async_class in (Thread, Process):
            self.do_test_execute(async_class)

    def do_test_execute(self, async_class):
        node_arg = AsyncNodeExample()

        observer = MagicMock()
        n = AsyncNodeWithArgExample(async_class=async_class, args=[node_arg])
        n.output.register_observer(observer)

        # TEST
        n.execute(node.NodeEvent('data'))

        # VERIFY
        time.sleep(0.1)

        self.assertEqual(1, observer.notify.call_count)
        self.assertEqual(('data', None), observer.notify.call_args[0][0])

        node_arg.execute(NodeEvent('node arg test'))
        time.sleep(EPS)
        n.execute(NodeEvent('data2'))
        time.sleep(EPS)

        self.assertEqual(2, observer.notify.call_count)
        self.assertEqual(('data2', 'result node arg test'), observer.notify.call_args[0][0])

        n.kill()
        node_arg.kill()

class AsyncNodeWithKwargExample(node.AsyncNode):

    def do_work(self, payload, kwarg1=None):
        print('AsyncNodeWithKwargExample(%s,kwarg1=%s)'%(payload, kwarg1))
        return payload, kwarg1


class AsyncNodeWithKwargTests(unittest.TestCase):

    def test_execute_multi(self):

        for async_class in (Thread, Process):
            self.do_test_execute(async_class)

    def do_test_execute(self, async_class):

        node_kwarg = AsyncNodeExample(async_class=async_class)

        observer = MagicMock()
        n = AsyncNodeWithKwargExample(kwargs={'kwarg1': node_kwarg})
        n.output.register_observer(observer)

        # TEST
        n.execute(node.NodeEvent('data'))

        # VERIFY
        time.sleep(0.1)

        print(observer.notify.call_args[0][0])
        self.assertEqual(1, observer.notify.call_count)
        self.assertEqual(('data', None), observer.notify.call_args[0][0])

        node_kwarg.execute(node.NodeEvent('node kwarg test'))
        time.sleep(EPS)
        n.execute(node.NodeEvent('data2'))
        time.sleep(EPS)

        self.assertEqual(2, observer.notify.call_count)
        self.assertEqual(('data2', 'result node kwarg test'), observer.notify.call_args[0][0])

        node_kwarg.kill()
        n.kill()

    def test_execute(self):

        # TEST
        self.node.execute(node.NodeEvent('data'))

        # VERIFY
        time.sleep(0.1)

        print(self.observer.notify.call_args[0][0])
        self.assertEqual(1, self.observer.notify.call_count)
        self.assertEqual(('data', None), self.observer.notify.call_args[0][0])

        self.node_kwarg.execute(node.NodeEvent('node kwarg test'))
        time.sleep(EPS)
        self.node.execute(node.NodeEvent('data2'))
        time.sleep(EPS)

        self.assertEqual(2, self.observer.notify.call_count)
        self.assertEqual(('data2', 'result node kwarg test'), self.observer.notify.call_args[0][0])


class MultiProcessingAsyncNodeTests(unittest.TestCase):

    def setUp(self):
        self.observer = MagicMock()
        self.node = AsyncNodeExample(async_class=multiprocessing.Process)
        self.node.output.register_observer(self.observer)

    def tearDown(self):
        self.node.kill()

    def test_execute(self):

        # TEST
        self.node.execute(node.NodeEvent('payload'))

        # VERIFY
        time.sleep(1)

        self.assertEqual(1, self.observer.notify.call_count)
        self.assertEqual('result payload', self.observer.notify.call_args[0][0])

    def test_get_value(self):

        # TEST
        self.node.execute(node.NodeEvent('payload'))

        # VERIFY
        time.sleep(EPS)
        self.assertEqual('result payload', self.node.get_value())


class BatchNodeInputTests(unittest.TestCase):

    def test_notify(self):
        for async_class in (Thread, Process):
            self.do_test_notify(async_class=async_class)

    def do_test_notify(self, async_class):

        observer = MagicMock()
        n = AsyncNodeExample(node.BatchNodeInput(2), async_class=async_class)
        n.output.register_observer(observer)

        # TEST
        n.input.notify([1, 2, 3, 4])

        # VERIFY
        time.sleep(EPS)

        self.assertEqual(2, observer.notify.call_count)
        self.assertEqual('result [1, 2]', observer.notify.call_args_list[0][0][0])
        self.assertEqual('result [3, 4]', observer.notify.call_args_list[1][0][0])

        n.kill()


class ListNodeInputTests(unittest.TestCase):

    def test_notify(self):

        for async_class in (Thread, Process):
            self.do_test_notify(async_class)

    def do_test_notify(self, async_class):

        # SETUP
        observer = MagicMock()
        n = AsyncNodeExample(node.ListNodeInput(), async_class=async_class)
        n.output.register_observer(observer)

        # TEST
        n.input.notify([1, 2, 3, 4])

        # VERIFY
        time.sleep(EPS)

        self.assertEqual(4, observer.notify.call_count)
        self.assertEqual('result 1', observer.notify.call_args_list[0][0][0])
        self.assertEqual('result 2', observer.notify.call_args_list[1][0][0])
        self.assertEqual('result 3', observer.notify.call_args_list[2][0][0])
        self.assertEqual('result 4', observer.notify.call_args_list[3][0][0])

        n.kill()

if __name__ == '__main__':
    unittest.main()
