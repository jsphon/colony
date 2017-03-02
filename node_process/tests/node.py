import unittest
from node_process import node
from mock import MagicMock
import time
import multiprocessing

EPS = 0.01


class AsyncNodeExample(node.AsyncNode):

    def do_work(self, payload):
        print('AsyncNodeExample doing work')
        return 'result %s'%payload


class AsyncNodeTests(unittest.TestCase):

    def setUp(self):
        self.observer = MagicMock()
        self.node = AsyncNodeExample()
        self.node.output.register_observer(self.observer)

    def tearDown(self):
        self.node.kill()

    def test_execute(self):

        # TEST
        self.node.execute('payload')

        # VERIFY
        time.sleep(EPS)

        self.assertEqual(1, self.observer.notify.call_count)
        self.assertEqual('result payload', self.observer.notify.call_args[0][0])

    def test_get_value(self):

        # TEST
        self.node.execute('payload')

        # VERIFY
        time.sleep(EPS)
        self.assertEqual('result payload', self.node.get_value())


class MultiProcessingAsyncNodeTests(unittest.TestCase):

    def setUp(self):
        self.observer = MagicMock()
        self.node = AsyncNodeExample(async_class=multiprocessing.Process)
        self.node.output.register_observer(self.observer)

    def tearDown(self):
        self.node.kill()

    def test_execute(self):

        # TEST
        self.node.execute('payload')

        # VERIFY
        time.sleep(1)

        self.assertEqual(1, self.observer.notify.call_count)
        self.assertEqual('result payload', self.observer.notify.call_args[0][0])

    def test_get_value(self):

        # TEST
        self.node.execute('payload')

        # VERIFY
        time.sleep(EPS)
        self.assertEqual('result payload', self.node.get_value())



class BatchNodeInputTests(unittest.TestCase):

    def setUp(self):
        self.observer = MagicMock()
        self.node = AsyncNodeExample(node.BatchNodeInput(2))
        self.node.output.register_observer(self.observer)

    def tearDown(self):
        self.node.kill()

    def test_notify(self):

        # TEST
        self.node.input.notify([1, 2, 3, 4])

        # VERIFY
        time.sleep(EPS)

        self.assertEqual(2, self.observer.notify.call_count)
        self.assertEqual('result [1, 2]', self.observer.notify.call_args_list[0][0][0])
        self.assertEqual('result [3, 4]', self.observer.notify.call_args_list[1][0][0])


class ListNodeInputTests(unittest.TestCase):

    def setUp(self):
        self.observer = MagicMock()
        self.node = AsyncNodeExample(node.ListNodeInput())
        self.node.output.register_observer(self.observer)

    def tearDown(self):
        self.node.kill()

    def test_notify(self):
        # TEST
        self.node.input.notify([1, 2, 3, 4])

        # VERIFY
        time.sleep(EPS)

        self.assertEqual(4, self.observer.notify.call_count)
        self.assertEqual('result 1', self.observer.notify.call_args_list[0][0][0])
        self.assertEqual('result 2', self.observer.notify.call_args_list[1][0][0])
        self.assertEqual('result 3', self.observer.notify.call_args_list[2][0][0])
        self.assertEqual('result 4', self.observer.notify.call_args_list[3][0][0])

#
#
# class BatchAsyncNodeTests(unittest.TestCase):
#
#     def setUp(self):
#         observable = MagicMock()
#         self.observer = MagicMock()
#         input_node = node.BatchNodeInput(observable, 1)
#         n = BatchAsyncNodeExample(input_node=input_node, num_threads=1)
#         n.register_observer(self.observer)
#         self.n = n
#
#     def tearDown(self):
#         self.n.kill()
#
#     def test_execute(self):
#
#         # TEST
#         self.n.execute(['payload1', 'payload2'])
#
#         # VERIFY
#         time.sleep(EPS)
#
#         self.assertEqual(2, self.observer.notify.call_count)
#         self.assertEqual('result payload', self.observer.notify.call_args[0][0])


if __name__ == '__main__':
    unittest.main()
