# -*- coding: utf-8 -*-
# Author: Dylan Jones
# Date:   2023-11-05

from datetime import datetime
from textwrap import dedent

from pytest import mark
from pytz import timezone

import ftmplt


@mark.parametrize(
    "name,spec,conv,fstr",
    [
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
    ],
)
def test_format_string(name, spec, conv, fstr):
    """Test building the format string."""
    assert ftmplt.format_string(name, spec, conv) == fstr


@mark.parametrize(
    "fstr,type_,base",
    [
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
        ("%a", datetime, None),
        ("%A", datetime, None),
        ("%w", datetime, None),
        ("%d", datetime, None),
        ("%b", datetime, None),
        ("%B", datetime, None),
        ("%m", datetime, None),
        ("%y", datetime, None),
        ("%Y", datetime, None),
        ("%H", datetime, None),
        ("%I", datetime, None),
        ("%p", datetime, None),
        ("%M", datetime, None),
        ("%S", datetime, None),
        ("%f", datetime, None),
        ("%z", datetime, None),
        ("%Z", datetime, None),
        ("%j", datetime, None),
        ("%U", datetime, None),
        ("%W", datetime, None),
        ("%c", datetime, None),
        ("%x", datetime, None),
        ("%X", datetime, None),
        ("%%", datetime, None),
        ("%G", datetime, None),
        ("%u", datetime, None),
        ("%V", datetime, None),
        ("%Y", datetime, None),
        ("%Y-%m", datetime, None),
        ("%Y-%b", datetime, None),
        ("%Y-%m-%d", datetime, None),
        ("%Y-%b-%d", datetime, None),
        ("%Y-%m-%d %H", datetime, None),
        ("%Y-%m-%d %H:%M", datetime, None),
        ("%Y-%m-%d %H:%M:%S", datetime, None),
    ],
)
def test_format_type(fstr, type_, base):
    """Test parsing the dtype of a format string."""
    t, b = ftmplt._format_type(fstr)
    assert t == type_
    assert b == base


def test_parse_str():
    x = "text"
    fstr = "Beginning {} end"
    s = fstr.format(x)
    parsed = ftmplt.parse(fstr, s)
    assert parsed[0] == x

    # Test string with spaces
    fstr = "Beginning {:<20} end"
    s = fstr.format(x)
    parsed = ftmplt.parse(fstr, s)
    assert parsed[0] == x


@mark.parametrize(
    "fmt",
    [
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
    ],
)
@mark.parametrize("value", [1, 2, 3, -1, -2, -3])
def test_parse_int(fmt, value):
    fstr = "Beginning {:" + fmt + "} end"
    s = fstr.format(value)
    parsed = ftmplt.parse(fstr, s)
    assert parsed[0] == value


@mark.parametrize(
    "fmt",
    [
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
    ],
)
@mark.parametrize("value", [1.123, 2.123, 3.123, -1.123, -2.123, -3.123])
def test_parse_float(fmt, value):
    fstr = "Beginning {:" + fmt + "} end"
    s = fstr.format(value)
    parsed = ftmplt.parse(fstr, s)
    assert parsed[0] == value


@mark.parametrize(
    "fmt",
    [
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
        "%a/%m/%y %H:%M:%S",
        "%A/%m/%y %H:%M:%S",
        "%w/%m/%y %H:%M:%S",
        "%d/%m/%y %H:%M:%S",
        "%d/%b/%y %H:%M:%S",
        "%d/%B/%y %H:%M:%S",
        "%d/%m/%y %H:%M:%S",
        "%d/%m/%y %H:%M:%S",
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y %I:%M:%S %p",
        "%d/%m/%Y %H:%M:%S.%f",
        "%d/%m/%Y %H:%M:%S %z",
        # "%d/%m/%Y %H:%M:%S %Z",
        "%d/%m/%j %H:%M:%S",
        "%c",
        "%x",
        "%X",
        "%a %V %G",
        "%A %V %G",
        "%w %V %G",
        "%u %V %G",
    ],
)
def test_parse_datetime(fmt):
    tz = timezone("Europe/Berlin")
    fstr = "Beginning {:" + fmt + "} end"
    now = datetime.now(tz=tz)
    s = fstr.format(now)
    parsed = ftmplt.parse(fstr, s)
    actual = datetime.strptime(now.strftime(fmt), fmt)
    assert parsed[0] == actual


def test_custom_formatter():
    class ArrayFormatter(ftmplt.CustomFormatter):
        def parse(self, text: str):
            values = text.split(",")
            return [int(v) for v in values]

        def format(self, value) -> str:
            return ", ".join([str(v) for v in value])

    array_formatter = ArrayFormatter("b")

    tmplt = "Beginning {a:d} and {b} end"
    data = {"a": 1, "b": [4, 5, 6]}
    s = ftmplt.format(tmplt, data, array_formatter)
    assert s == "Beginning 1 and 4, 5, 6 end"
    parsed = ftmplt.parse(tmplt, s, array_formatter)
    assert parsed["a"] == data["a"]
    assert parsed["b"] == data["b"]


def test_default_fields():
    fstr = "Beginning {} {:d} {:f} end"
    a, b, c = "text", 1, 1.1
    s = fstr.format(a, b, c)
    parsed = ftmplt.parse(fstr, s)
    assert parsed[0] == a
    assert parsed[1] == b
    assert parsed[2] == c


def test_indexed_fields():
    fstr = "Beginning {0} {1:d} {2:f} end"
    a, b, c = "text", 1, 1.1
    s = fstr.format(a, b, c)
    parsed = ftmplt.parse(fstr, s)
    assert parsed[0] == a
    assert parsed[1] == b
    assert parsed[2] == c


def test_named_fields():
    fstr = "Beginning {a} {b:d} {c:f} end"
    a, b, c = "text", 1, 1.1
    s = fstr.format(a=a, b=b, c=c)
    parsed = ftmplt.parse(fstr, s)
    assert parsed["a"] == a
    assert parsed["b"] == b
    assert parsed["c"] == c


def test_mixed_fields():
    fstr = "Beginning {0} {1:d} {c:f} end"
    a, b, c = "text", 1, 1.1
    s = fstr.format(a, b, c=c)
    parsed = ftmplt.parse(fstr, s)
    assert parsed[0] == a
    assert parsed[1] == b
    assert parsed["c"] == c


def test_double_fields():
    fstr = "Beginning {a:d} {b:d} {a:d} end"
    a, b = 1, 2
    s = fstr.format(a=a, b=b)
    assert s == "Beginning 1 2 1 end"
    parsed = ftmplt.parse(fstr, s)
    assert len(parsed) == 2
    assert parsed["a"] == a
    assert parsed["b"] == b


def test_multiline_text():
    fstr = dedent(
        """Beginning
        {0}
        {1:d}
        {c:f}
        end"""
    )
    a, b, c = "text", 1, 1.1
    s = fstr.format(a, b, c=c)
    parsed = ftmplt.parse(fstr, s)
    assert parsed[0] == a
    assert parsed[1] == b
    assert parsed["c"] == c


def test_multiline_field():
    tmplt = dedent(
        """\
        Beginning
        {}
        end"""
    )
    text = dedent(
        """\
        Beginning
        This is a text
        that spans multiple lines
        in the middle of the string
        end"""
    )
    parsed = ftmplt.parse(tmplt, text)
    s = "This is a text\nthat spans multiple lines\nin the middle of the string"
    assert parsed[0] == s


def test_multiline_field_start():
    tmplt = dedent(
        """\
        {}
        end"""
    )
    text = dedent(
        """\
        This is a text
        that spans multiple lines
        at the start of the string
        end"""
    )
    parsed = ftmplt.parse(tmplt, text)
    s = "This is a text\nthat spans multiple lines\nat the start of the string"
    assert parsed[0] == s


def test_multiline_field_end():
    tmplt = dedent(
        """\
        Beginning
        {}
        """
    )
    text = dedent(
        """\
        Beginning
        This is a text
        that spans multiple lines
        at the end of the string
        """
    )
    parsed = ftmplt.parse(tmplt, text)
    s = "This is a text\nthat spans multiple lines\nat the end of the string"
    assert parsed[0] == s
