import os
import tempfile
from subprocess import call

import pygraphviz as pgv


def display_graph(g):
    """ Display the graph locally
        Currently only works on Ubuntu
    """

    basename = '%s.png' % tempfile.TemporaryFile().name
    path = os.path.join(tempfile.tempdir, basename)
    gg = g.copy()
    gg.layout()
    gg.draw(path)

    call(['xdg-open', path])


if __name__ == '__main__':
    A = pgv.AGraph()

    A.add_edge(1, 2)
    A.add_edge(2, 3)
    A.add_edge(1, 3)
    display_graph(A)
