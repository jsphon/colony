from colony.node import Graph, Node
from colony.observer import RememberingObserver


class ExampleTargetClass(object):
    def __init__(self, c):
        print('Initialising target_funcClass')
        self.data = set([c])
        print('data is %s' % str(self.data))

    def execute(self, x):
        self.data.add(x)
        return self.data


if __name__=='__main__':

    n = Node(target_class=target_funcClass, target_class_args=(0,))
    n.start()

    n.notify(1)
    self.assertEqual({0, 1}, n.get_value())

    n.notify(2)
    self.assertEqual({0, 1, 2}, n.get_value())

    n.notify(3)
    self.assertEqual({0, 1, 2, 3}, n.get_value())