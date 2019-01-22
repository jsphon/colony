import json
import os
import tempfile

DEFAULT_FOLDER = tempfile.gettempdir()


class PersistentVariable(object):
    def __init__(self, name, folder):
        self.name = name
        self.folder = folder or DEFAULT_FOLDER
        self.path = os.path.join(self.folder, name)
        self.value = None
        self.refresh()

    def refresh(self):
        if os.path.isfile(self.path):
            with open(self.path) as f:
                try:
                    self.value = json.load(f)
                except json.decoder.JSONDecodeError as e:
                    print('Could not decode %s' % self.path)

    def set_value(self, value):
        self.value = value
        with open(self.path, 'w') as f:
            json.dump(value, f)

    def get_value(self):
        return self.value


if __name__ == '__main__':
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
