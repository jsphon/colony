import time
import unittest
from multiprocessing import Process
from threading import Thread

from mock import MagicMock

from node_process.node import AsyncNode, NodeEvent, ListNodeInput, BatchNodeInput

EPS = 0.01


def basic_target(payload):
    return 'result %s' % payload


def thread_target(payload):
    return 'thread_target(%s)'%payload


def target_with_arg(payload, arg):
    return payload, arg


def target_with_kwarg(payload, kwarg1=None):
    return payload, kwarg1


class AsyncNodeTests(unittest.TestCase):

    def test_execute(self):
        for async_class in (Thread, Process):
            print('=== Executing test with async_class=%s ==='%async_class)
            self.do_test_execute(async_class)

    def do_test_execute(self, async_class):

        observer = MagicMock()
        n = AsyncNode(target=basic_target, async_class=async_class)
        n.output.register_observer(observer)

        child = AsyncNode(target=thread_target, async_class=Thread)
        n.output.register_observer(child.input)

        time.sleep(EPS)

        # TEST
        n.execute(NodeEvent('payload'))

        # VERIFY
        time.sleep(EPS)

        self.assertEqual('thread_target(result payload)', child.get_value())

        #self.assertEqual(1, observer.notify.call_count)
        #self.assertEqual('result payload', observer.notify.call_args[0][0].payload)

        # Tear Down
        print('Killing')
        n.kill()

    def test_get_value(self):
        for async_class in (Thread, Process):
            self.do_test_get_value(async_class)

    def do_test_get_value(self, async_class):

        n = AsyncNode(target=basic_target, async_class=async_class)
        # TEST
        n.execute(NodeEvent('payload'))

        # VERIFY
        time.sleep(EPS)
        self.assertEqual('result payload', n.get_value())

        n.kill()


class AsyncNodeWithArgTests(unittest.TestCase):

    def test_execute(self):
        for async_class in (Thread, Process):
            self.do_test_execute(async_class)

    def do_test_execute(self, async_class):
        node_arg = AsyncNode(target=basic_target, async_class=async_class)

        observer = MagicMock()
        n = AsyncNode(target=target_with_arg, async_class=async_class, args=[node_arg])
        n.output.register_observer(observer)

        # TEST
        n.execute(NodeEvent('data'))

        # VERIFY
        time.sleep(0.1)

        self.assertEqual(1, observer.notify.call_count)
        self.assertEqual(('data', None), observer.notify.call_args[0][0].payload)

        node_arg.execute(NodeEvent('node arg test'))
        time.sleep(EPS)
        n.execute(NodeEvent('data2'))
        time.sleep(EPS)

        self.assertEqual(2, observer.notify.call_count)
        self.assertEqual(('data2', 'result node arg test'), observer.notify.call_args[0][0].payload)

        n.kill()
        node_arg.kill()


class AsyncNodeWithKwargTests(unittest.TestCase):
    def test_execute_multi(self):
        for async_class in (Thread, Process):
            self.do_test_execute(async_class)

    def do_test_execute(self, async_class):
        node_kwarg = AsyncNode(target=basic_target, async_class=async_class)

        observer = MagicMock()
        n = AsyncNode(target=target_with_kwarg, kwargs={'kwarg1': node_kwarg})
        n.output.register_observer(observer)

        # TEST
        n.execute(NodeEvent('data'))

        # VERIFY
        time.sleep(0.1)

        self.assertEqual(1, observer.notify.call_count)
        self.assertEqual(('data', None), observer.notify.call_args[0][0].payload)

        node_kwarg.execute(NodeEvent('node kwarg test'))
        time.sleep(EPS)
        n.execute(NodeEvent('data2'))
        time.sleep(EPS)

        self.assertEqual(2, observer.notify.call_count)
        self.assertEqual(('data2', 'result node kwarg test'), observer.notify.call_args[0][0].payload)

        node_kwarg.kill()
        n.kill()


class BatchNodeInputTests(unittest.TestCase):
    def test_notify(self):
        for async_class in (Thread, Process):
            self.do_test_notify(async_class=async_class)

    def do_test_notify(self, async_class):
        observer = MagicMock()
        n = AsyncNode(target=basic_target, node_input=BatchNodeInput(2), async_class=async_class)
        n.output.register_observer(observer)

        # TEST
        n.input.notify([1, 2, 3, 4])

        # VERIFY
        time.sleep(EPS)

        self.assertEqual(2, observer.notify.call_count)
        self.assertEqual('result [1, 2]', observer.notify.call_args_list[0][0][0].payload)
        self.assertEqual('result [3, 4]', observer.notify.call_args_list[1][0][0].payload)

        n.kill()


class ListNodeInputTests(unittest.TestCase):
    def test_notify(self):
        for async_class in (Thread, Process):
            self.do_test_notify(async_class)

    def do_test_notify(self, async_class):
        # SETUP
        observer = MagicMock()
        n = AsyncNode(target=basic_target, node_input=ListNodeInput(), async_class=async_class)
        n.output.register_observer(observer)

        # TEST
        n.input.notify([1, 2, 3, 4])

        # VERIFY
        time.sleep(EPS)

        self.assertEqual(4, observer.notify.call_count)
        self.assertEqual('result 1', observer.notify.call_args_list[0][0][0].payload)
        self.assertEqual('result 2', observer.notify.call_args_list[1][0][0].payload)
        self.assertEqual('result 3', observer.notify.call_args_list[2][0][0].payload)
        self.assertEqual('result 4', observer.notify.call_args_list[3][0][0].payload)

        n.kill()


if __name__ == '__main__':
    unittest.main()
