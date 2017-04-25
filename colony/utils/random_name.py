import os
import tempfile


def random_name():
    return os.path.basename(tempfile.NamedTemporaryFile().name)