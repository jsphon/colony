import random
import string
import time
import zipfile
from datetime import datetime
from io import BytesIO

from colony.node import Graph
from colony.utils.timer import Timer


def download_data(seed, n=10000):
    """Dummy Downloading Function"""
    random.seed(seed)
    time.sleep(1.0)
    result = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(n))
    print('Downloaded data of len %i for seed %s, data=%s...' % (len(result), seed, result[:10]))
    return seed, result


def save_data(arg):
    """Dummy Save Data Function"""
    seed, data = arg
    time.sleep(1)
    print('Saving seed %s, data=%s...' % (seed, data[:10]))

    f = BytesIO()
    with zipfile.ZipFile(f, 'a', zipfile.ZIP_DEFLATED) as zf:
        archive_name = '%s' % (str(datetime.utcnow()))
        zf.writestr(archive_name, data)


if __name__ == '__main__':

    col = Graph()

    download_node = col.add_thread_node(target=download_data)
    saving_node = col.add_thread_node(target=save_data, num_threads=1, node_args=download_node)

    col.start()

    with Timer('downloading'):
        download_node.notify_items(range(10))

        col.stop()

    print('Finished')
