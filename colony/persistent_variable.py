import json
import os

DEFAULT_PATH = '/tmp/'


class PersistentVariable(object):

    def __init__(self, name, folder=DEFAULT_PATH):
        self.name = name
        self.folder = folder
        self.path = os.path.join(folder, name)
        self.value = None
        self.refresh()

    def refresh(self):
        if os.path.isfile(self.path):
            with open(self.path) as f:
                self.value = json.load(f)

    def set_value(self, value):
        self.value = value
        with open(self.path, 'w') as f:
            json.dump(value, f)

    def get_value(self):
        return self.value


if __name__=='__main__':

    p = PersistentVariable('hello')

    p.set_value('hello')

    print(p.get_value())

    p.set_value('world')

    print(p.get_value())

    p2 = PersistentVariable('hello')

    print(p2.get_value())

    p2.set_value('foo')

    p.refresh()
    print(p.get_value())
