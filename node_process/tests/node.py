import unittest
from node_process import node
from mock import MagicMock


class NodeTests(unittest.TestCase):

    def test_execute(self):
        observable = MagicMock()
        payload = MagicMock()

        n = node.Node(observable)

        with self.assertRaises(NotImplementedError) as e:
            n.execute(payload)

        self.assertEqual('do_work not implemented', str(e.exception))


class AsyncNodeTests(unittest.TestCase):

    def test_execute(self):
        observable = MagicMock()
        payload = MagicMock()

        n = node.AsyncNode(observable)

        n.execute(payload)
        # with self.assertRaises(NotImplementedError) as e:
        #     n.execute(payload)
        #
        # self.assertEqual('do_work not implemented', str(e.exception))
        #



if __name__ == '__main__':
    unittest.main()
