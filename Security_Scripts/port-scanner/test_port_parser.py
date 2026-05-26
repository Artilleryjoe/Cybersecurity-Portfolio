import importlib.util
from pathlib import Path

import pytest

MODULE_PATH = Path(__file__).with_name("port-scanner.py")
spec = importlib.util.spec_from_file_location("port_scanner", MODULE_PATH)
port_scanner = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(port_scanner)


def test_parse_ports_accepts_spaced_comma_list():
    assert list(port_scanner.parse_ports("22, 80,443")) == [22, 80, 443]


def test_parse_ports_rejects_invalid_port_range_value():
    with pytest.raises(ValueError):
        list(port_scanner.parse_ports("0-22"))


def test_parse_ports_rejects_malformed_range():
    with pytest.raises(ValueError):
        list(port_scanner.parse_ports("1-2-3"))
