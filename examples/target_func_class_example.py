from colony.node import Node


class ExampleTargetClass(object):
    def __init__(self, c):
        print('Initialising ExampleTargetClass')
        self.data = set([c])
        print('data is %s' % str(self.data))

    def execute(self, x):
        self.data.add(x)
        return self.data


if __name__ == '__main__':
    n = Node(target_class=ExampleTargetClass, target_class_args=(0,))
    n.start()

    n.notify(1)
    # Expect {0, 1}
    print(n.get_value())

    n.notify(2)
    # Expect {0, 1, 2}
    print(n.get_value())

    n.notify(3)
    # Expect {0, 1, 2, 3}
    print(n.get_value())
