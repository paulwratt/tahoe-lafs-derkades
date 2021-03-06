"""
Ported to Python 3.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from future.utils import PY2
if PY2:
    from future.builtins import filter, map, zip, ascii, chr, hex, input, next, oct, open, pow, round, super, bytes, dict, list, object, range, str, max, min  # noqa: F401

import sys
from os.path import join

from twisted.internet.error import ProcessTerminated

from . import util

import pytest_twisted


@pytest_twisted.inlineCallbacks
def test_upload_immutable(reactor, temp_dir, introducer_furl, flog_gatherer, storage_nodes, request):

    edna = yield util._create_node(
        reactor, request, temp_dir, introducer_furl, flog_gatherer, "edna",
        web_port="tcp:9983:interface=localhost",
        storage=False,
        needed=3,
        happy=7,
        total=10,
    )
    util.await_client_ready(edna)

    node_dir = join(temp_dir, 'edna')

    # upload a file, which should fail because we have don't have 7
    # storage servers (but happiness is set to 7)
    proto = util._CollectOutputProtocol()
    reactor.spawnProcess(
        proto,
        sys.executable,
        [
            sys.executable, '-b', '-m', 'allmydata.scripts.runner',
            '-d', node_dir,
            'put', __file__,
        ]
    )
    try:
        yield proto.done
        assert False, "should raise exception"
    except Exception as e:
        assert isinstance(e, ProcessTerminated)

    output = proto.output.getvalue()
    assert b"shares could be placed on only" in output
