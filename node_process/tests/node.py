import unittest
from node_process import node
from mock import MagicMock
import time

EPS = 0.01

class NodeTests(unittest.TestCase):

    def test_execute(self):
        observable = MagicMock()
        payload = MagicMock()

        n = node.Node(observable)

        with self.assertRaises(NotImplementedError) as e:
            n.execute(payload)

        self.assertEqual('do_work not implemented', str(e.exception))


class AsyncNodeExample(node.AsyncNode):

    def do_work(self, payload):
        return 'result %s'%payload


class AsyncNodeTests(unittest.TestCase):


    def setUp(self):
        observable = MagicMock()
        self.observer = MagicMock()
        n = AsyncNodeExample(observable)
        n.register_observer(self.observer)
        self.n = n

    def tearDown(self):
        self.n.kill()

    def test_execute(self):

        # TEST
        self.n.execute('payload')

        # VERIFY
        time.sleep(EPS)

        self.assertEqual(1, self.observer.notify.call_count)
        self.assertEqual('result payload', self.observer.notify.call_args[0][0])

    def test_get_value(self):

        # TEST
        self.n.execute('payload')

        # VERIFY
        time.sleep(EPS)
        self.assertEqual('result payload', self.n.get_value())

if __name__ == '__main__':
    unittest.main()
