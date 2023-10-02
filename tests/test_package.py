from __future__ import annotations

import importlib.metadata

import bad_tools as m


def test_version():
    assert importlib.metadata.version("bad_tools") == m.__version__
