# -*- coding: utf-8 -*-
# Author: Dylan Jones
# Date:   2023-11-05

from textwrap import dedent
from pytest import mark, fixture
from datetime import datetime
import ftmplt


@mark.parametrize("name,spec,conv,fstr", [
    (None, None, None, "{}"),
    ("", "", "", "{}"),
    ("name", "", "", "{name}"),
    ("name", None, None, "{name}"),
    (None, "spec", "", "{:spec}"),
    ("", "spec", "", "{:spec}"),
    ("name", "spec", None, "{name:spec}"),
    ("name", "spec", "", "{name:spec}"),
    ("", "spec", "conv", "{!conv:spec}"),
    ("name", "spec", "conv", "{name!conv:spec}"),
    ("name", "", "conv", "{name!conv}"),
])
def test_format_string(name, spec, conv, fstr):
    """Test building the format string."""
    assert ftmplt.format_string(name, spec, conv) == fstr


@mark.parametrize("fstr,type_,base", [
    ("", None, None),
    ("b", int, 2),
    ("2b", int, 2),
    ("02b", int, 2),
    ("+02b", int, 2),
    ("d", int, None),
    ("2d", int, None),
    ("02d", int, None),
    ("+02d", int, None),
    ("o", int, 8),
    ("2o", int, 8),
    ("02o", int, 8),
    ("+02o", int, 8),
    ("x", int, 16),
    ("2x", int, 16),
    ("02x", int, 16),
    ("+02x", int, 16),
    ("X", int, 16),
    ("2X", int, 16),
    ("02X", int, 16),
    ("+02X", int, 16),
    ("e", float, None),
    (".2e", float, None),
    ("2.2e", float, None),
    ("02.2e", float, None),
    ("+02.2e", float, None),
    ("E", float, None),
    (".2E", float, None),
    ("2.2E", float, None),
    ("02.2E", float, None),
    ("+02.2E", float, None),
    ("f", float, None),
    (".2f", float, None),
    ("2.2f", float, None),
    ("02.2f", float, None),
    ("+02.2f", float, None),
    ("F", float, None),
    (".2F", float, None),
    ("2.2F", float, None),
    ("02.2F", float, None),
    ("+02.2F", float, None),
    ("g", float, None),
    ("2g", float, None),
    ("+2g", float, None),
    ("G", float, None),
    ("2G", float, None),
    ("+2G", float, None),
    ("%", float, None),
    (".2%", float, None),
    ("2.2%", float, None),
    ("02.2%", float, None),
    ("+02.2%", float, None),
    ("%Y", datetime, None),
    ("%Y-%m", datetime, None),
    ("%Y-%b", datetime, None),
    ("%Y-%m-%d", datetime, None),
    ("%Y-%b-%d", datetime, None),
    ("%Y-%m-%d %H", datetime, None),
    ("%Y-%m-%d %H:%M", datetime, None),
    ("%Y-%m-%d %H:%M:%S", datetime, None),
])
def test_format_type(fstr, type_, base):
    """Test parsing the dtype of a format string."""
    t, b = ftmplt.format_type(fstr)
    assert t == type_
    assert b == base


def test_parse_str():
    fstr = "Beginning {} end"
    s = fstr.format("text")
    parsed = ftmplt.parse(fstr, s)
    assert parsed[0] == "text"


@mark.parametrize("fmt", [
    "b",
    "2b",
    "02b",
    "+02b",
    "d",
    "2d",
    "02d",
    "+02d",
    "o",
    "2o",
    "02o",
    "+02o",
    "x",
    "2x",
    "02x",
    "+02x",
    "X",
    "2X",
    "02X",
    "+02X",
])
@mark.parametrize("value", [1, 2, 3, -1, -2, -3])
def test_parse_int(fmt, value):
    fstr = "Beginning {:" + fmt + "} end"
    s = fstr.format(value)
    parsed = ftmplt.parse(fstr, s)
    assert parsed[0] == value


@mark.parametrize("fmt", [
    "e",
    ".4e",
    "2.4e",
    "09.4e",
    "+09.4e",
    "E",
    ".4E",
    "2.4E",
    "09.4E",
    "+09.4E",
    "f",
    ".4f",
    "2.4f",
    "09.4f",
    "+09.4f",
    "F",
    ".4F",
    "2.4F",
    "09.4F",
    "+09.4F",
    "g",
    ".4g",
    "2.4g",
    "09.4g",
    "+09.4g",
    "G",
    ".4G",
    "2.4G",
    "09.4G",
    "+09.4G",
    "%",
    ".4%",
    "2.4%",
    "09.4%",
    "+09.4%",
])
@mark.parametrize("value", [1.123, 2.123, 3.123, -1.123, -2.123, -3.123])
def test_parse_float(fmt, value):
    fstr = "Beginning {:" + fmt + "} end"
    s = fstr.format(value)
    parsed = ftmplt.parse(fstr, s)
    assert parsed[0] == value


@mark.parametrize("fmt", [
    "%Y",
    "%Y-%m",
    "%Y-%b",
    "%Y-%m-%d",
    "%Y-%b-%d",
    "%H",
    "%H:%M",
    "%H:%M:%S",
    "%Y-%m-%d %H",
    "%Y-%m-%d %H:%M",
    "%Y-%m-%d %H:%M:%S",
])
def test_parse_datetime(fmt):
    fstr = "Beginning {:" + fmt + "} end"
    now = datetime.now()
    s = fstr.format(now)
    parsed = ftmplt.parse(fstr, s)
    actual = datetime.strptime(now.strftime(fmt), fmt)
    assert parsed[0] == actual
