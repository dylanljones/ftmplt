# -*- coding: utf-8 -*
# Author: Dylan Jones
# Date:   2023-06-22

"""fTmplt: Simple string parsing and formatting using Python's format strings

This project is similar to [parse](https://github.com/r1chardj0n3s/parse),
but emphasizes on format strings that are both parsable and formattable.
This means only format specifiers that are both valid for parsing and formatting
are supported. It was originally developed to parse and format input and output
files for various computational physics libraries.

Examples
--------

Define a template using the Python format string syntax.
From there it's a simple thing to parse, search or format a string.

>>> import ftmplt
>>> tpl = "Hello, my name is {name} and I am {age:d} years old."
>>> s = "Hello, my name is John and I am 42 years old."

Parse all parameters from a string:

>>> ftmplt.parse(tpl, s)
{'name': 'John', 'age': 42}

or search a string for some pattern:

>>> ftmplt.search(tpl, s, "name")
('John', (19, 23))

>>> ftmplt.search(tpl, s, "age")
(42, (33, 35))

If you're going to use the same pattern to match lots of strings you can use the
``Template`` object. Once initialised, the template object can be used similarly
to the functions above:
>>> import ftmplt
>>> template = ftmplt.Template("Hello, my name is {name} and I am {age:d} years old.")
>>> s = "Hello, my name is John and I am 42 years old."

>>> template.parse(s)
{'name': 'John', 'age': 42}

>>> template.search("name", s)
('John', (19, 23))

>>> template.format({"name": "John", "age": 42})
"Hello, my name is John and I am 42 years old."
"""

import re
import string
import dataclasses
from datetime import datetime
from typing import List, Tuple, Optional, Union, Dict, Any

__all__ = ["Template", "parse", "search", "format"]

Key = Union[int, str]
Result = Dict[Key, Any]
SearchResult = Tuple[Any, Tuple[int, int]]

# Integer format specifiers
FMT_INT = (
    "b",  # Binary format. Outputs the number in base 2.
    "d",  # Decimal Integer. Outputs the number in base 10.
    "o",  # Octal format. Outputs the number in base 8.
    "x",  # Hex format. Outputs the number in base 16, using lower-case letters.
    "X",  # Hex format. Outputs the number in base 16, using upper-case letters.
    # In case '#' is specified, the prefix '0x' will be upper-cased to '0X'.
)

# Float format specifiers
FMT_FLOAT = (
    "e",  # Exponent notation. Prints the number in scientific notation using the
    # letter 'e' to indicate the exponent.
    "E",  # Exponent notation. Same as 'e' except it uses an upper case 'E'.
    "f",  # Fixed-point notation. Displays the number as a fixed-point number.
    "F",  # Fixed-point notation. Same as 'f' but converts nan to NAN and inf to INF.
    "g",  # General format. For a given precision p >= 1, this rounds the number to
    # p significant digits and then formats the result in either fixed-point
    # format or in scientific notation, depending on its magnitude.
    "G",  # General format. Same as 'g' except switches to 'E' if the number gets
    # too large. The representations of infinity and NaN are uppercased, too.
    "%",  # Percentage. Multiplies the number by 100 and displays in fixed ('f') format
)

# Datetime format specifiers
FMT_DT = [
    "%a",
    "%A",
    "%w",
    "%d",
    "%b",
    "%B",
    "%m",
    "%y",
    "%Y",
    "%H",
    "%I",
    "%p",
    "%M",
    "%S",
    "%f",
    "%z",
    "%Z",
    "%j",
    "%U",
    "%W",
    "%c",
    "%x",
    "%X",
    "%%",
    "%G",
    "%u",
    "%V",
    "%d/%m/%y %H:%M:%S.%f",
]


@dataclasses.dataclass
class FormatField:
    """Dataclass for a single format-string field."""

    name: str
    spec: str
    conv: str
    fstr: str
    type: type
    base: int
    pattern: re.Pattern
    group_name: str


def format_string(name: str = None, spec: str = None, conv: str = None) -> str:
    """Return format string for a single field

    Parameters
    ----------
    name : str, optional
        Name of the field, by default None
    spec : str, optional
        Format specifier, by default None
    conv : str, optional
        Conversion character, by default None

    Returns
    -------
    fstr : str
    """
    if isinstance(name, int):
        name = str(name)
    fstr = name or ""
    if conv:
        fstr += f"!{conv}"
    if spec:
        fstr += f":{spec}"
    return "{" + fstr + "}"


def _format_type(spec: str = None) -> Optional[Tuple[Optional[type], Optional[int]]]:
    """Return type of format specifier

    Parameters
    ----------
    spec : str, optional
        Format specifier, by default None

    Returns
    -------
    type_ : type
    """
    if not spec:
        return None, None
    typechar = spec[-1]
    if not typechar.isalpha() and typechar != "%":
        return None, None

    if any(spec.endswith(fmt) for fmt in FMT_DT):
        return datetime, None

    if typechar.lower() in FMT_INT:
        base = None
        if typechar.lower() == "b":
            base = 2
        elif typechar.lower() == "o":
            base = 8
        elif typechar.lower() == "x":
            base = 16
        return int, base
    if typechar.lower() in FMT_FLOAT:
        return float, None

    if "%" in spec[:-1]:
        return datetime, None

    supported = FMT_INT + FMT_FLOAT
    raise ValueError(
        f"Type {typechar} of format specifier {spec} not supported. "
        f"Valid types are: {supported}"
    )


def _convert_type(field: FormatField, value: Any) -> Any:
    """Convert value to given type"""
    # Parse int
    if field.type is int:
        return int(value, field.base) if field.base else int(value)
    # Parse float
    if field.type is float:
        if field.spec.endswith("%"):
            value = float(value[:-1]) / 100
        else:
            value = float(value)
        return value
    # Parse datetime
    if field.type is datetime:
        return datetime.strptime(value, field.spec)
    # Parse string
    return value.strip()


def _split_data(data: Dict[Key, Any]) -> Tuple[Tuple[Any], Dict[str, Any]]:
    """Split data into args and kwargs

    Parameters
    ----------
    data : dict[int|str, Any]
        Data to split

    Returns
    -------
    args : tuple[Any]
        Positional arguments
    kwargs : dict[str, Any]
        Keyword arguments
    """
    args, kwargs = list(), data.copy()
    for key, val in data.items():
        if isinstance(key, int):
            args.append(val)
            del kwargs[key]
    return tuple(args), kwargs


def _compile_fields(
    template: str, ignore_case: bool = False, flags: Union[int, re.RegexFlag] = None
) -> Tuple[List[FormatField], re.Pattern]:
    """Compile format fields in template string and generate RegEx pattern

    Parameters
    ----------
    template : str
        Template string
    ignore_case : bool, optional
        Ignore case when matching fields, by default False
    flags : int or re.RegexFlag, optional
        Additional RegEx flags

    Returns
    -------
    fields : list[FormatField]
        List of format-string fields
    pattern : re.Pattern
        Compiled RegEx pattern for parsing text with the template.
    """
    if flags is None:
        flags = 0
    if ignore_case:
        flags |= re.IGNORECASE

    template = template.strip()
    items = list(string.Formatter().parse(template))
    if any(x is not None for x in items[-1][1:]):
        # Last char belongs to fstring, add empty end char
        items.append(("", None, None, None))

    fields = list()
    text_suffix = ""
    pattern_str_full = ""
    empty, pos = False, 0
    group_names = set()
    for i in range(len(items) - 1):
        text, name, spec, conv = items[i]
        if not name:
            group_name = f"_pos_{pos}"
            name = str(pos)
            pos += 1
            empty = True
        elif name.isdigit():
            if empty:
                raise ValueError(
                    "cannot switch from automatic field numbering "
                    "to manual field specification"
                )
            group_name = f"_pos_{name}"
            # name = ""
        else:
            group_name = name

        # Initialize field
        fstr = format_string(name, spec, conv)
        text_suffix = items[i + 1][0]
        type_, base = _format_type(spec)
        if group_name in group_names:
            group = rf"((\n|.)*)"  # noqa: F541
        else:
            group = rf"(?P<{group_name}>(\n|.)*?)"
            pattern_str = re.escape(text) + group + re.escape(text_suffix)
            pattern = re.compile(pattern_str, flags=flags)
            field = FormatField(
                name, spec, conv, fstr, type_, base, pattern, group_name
            )
            fields.append(field)

        # Update full regex pattern string
        pattern_str_full += re.escape(text) + group
        group_names.add(group_name)

    # Use last text suffix for end of string
    pattern_str_full = pattern_str_full + re.escape(text_suffix)
    pattern_full = re.compile(pattern_str_full + r"$", flags=flags)

    return fields, pattern_full


def _parse(
    fields: List[FormatField], pattern: re.Pattern, text: str
) -> Tuple[Result, Dict[Key, Tuple[int, int]]]:
    """Parse text with format-string fields

    Parameters
    ----------
    fields : List[FormatField]
        List of format-string fields
    pattern : re.Pattern
        Compiled RegEx pattern for parsing text with the template.
    text : str
        Text to parse

    Returns
    -------
    data : dict[str|int, Any]
        Parsed data as a dictionary
    spans : dict[str|int, tuple[int, int]]
        Spans of parsed data
    """
    text = text.strip()
    match = pattern.match(text)
    raw_data = match.groupdict()
    data = dict()
    spans = dict()
    for field in fields:
        # Try to convert to int or float
        k = field.name
        if k.isdigit():
            k = int(k)
        data[k] = _convert_type(field, raw_data[field.group_name])
        # Get span of field
        spans[k] = match.span(field.group_name)

    return data, spans


def _get_field(fields: List[FormatField], item: Key) -> FormatField:
    """Get field by name or index

    Parameters
    ----------
    fields : list[FormatField]
        List of format-string fields
    item : str or int
        Name or index of field

    Returns
    -------
    field : FormatField
    """
    item = str(item)
    for field in fields:
        if field.name == item:
            return field
    raise KeyError(f"Field {item} not found")


def _search(fields: List[FormatField], item: Key, text: str) -> SearchResult:
    """Search for a single field in text

    Parameters
    ----------
    fields : list[FormatField]
        List of format-string fields
    item : str or int
        Name or index of field
    text : str
        Text to search

    Returns
    -------
    value : Any
        Value of field
    span : tuple[int, int]
        Span of field in text
    """
    text = text.strip()
    field = _get_field(fields, item)
    match = field.pattern.search(text)
    if match is None:
        raise ValueError(f"Field {item} not found in text")
    value = match.group(field.group_name)
    value = _convert_type(field, value)
    span = match.span(field.group_name)
    return value, span


def _format(template: str, data: Result) -> str:
    """Generated formated string from template and data

    Parameters
    ----------
    template : str
        Template string
    data : dict[str|int, Any]
        Data to format

    Returns
    -------
    text : str
        Formatted text
    """
    args, kwargs = _split_data(data)
    return template.format(*args, **kwargs)


class Template:
    """String template for parsing and formatting"""

    def __init__(
        self,
        template: str,
        ignore_case: bool = False,
        flags: Union[int, re.RegexFlag] = None,
    ):
        self.template = template
        self._fields, self._pattern = _compile_fields(template, ignore_case, flags)

    @property
    def fields(self) -> List[FormatField]:
        """List of format-string fields"""
        return self._fields

    @property
    def named_fields(self):
        return {field.name: field for field in self.fields if not field.name.isdigit()}

    @property
    def positional_fields(self):
        return {field.name: field for field in self.fields if field.name.isdigit()}

    def get_field(self, key: Key) -> FormatField:
        """Get field by name or index

        Parameters
        ----------
        key : str or int
            Name or index of field

        Returns
        -------
        field : FormatField
        """
        if isinstance(key, int):
            key = f"_pos_{key}"
        for field in self._fields:
            if field.group_name == key:
                return field
        raise _get_field(self._fields, key)

    def format(self, data) -> str:
        """Format data using template string

        Parameters
        ----------
        data : dict[str|int, Any]
            Data to format

        Returns
        -------
        text : str
            Formatted text

        Examples
        --------
        Named format fields:
        >>> template = Template("My name is {name} and I am {age:d} years old")
        >>> template.format({"name": "John", "age": 42})
        'My name is John and I am 42 years old'

        Indexed format fields:
        >>> template = Template("My name is {0} and I am {1:d} years old")
        >>> template.format({0: "John", 1: 42})
        'My name is John and I am 42 years old'

        Empty format fields:
        >>> template = Template("My name is {} and I am {:d} years old")
        >>> template.format({0: "John", 1: 42})
        'My name is John and I am 42 years old'

        Mixed format fields:
        >>> template = Template("My name is {} and I am {age:d} years old")
        >>> template.format({0: "John", "age": 42})
        'My name is John and I am 42 years old'
        """
        return _format(self.template, data)

    def parse(self, text: str) -> Result:
        """Parse text using template string

        Parameters
        ----------
        text : str
            Text to parse

        Returns
        -------
        data : dict[str|int, Any]
            Parsed data as a dictionary

        Examples
        --------

        Examples
        --------
        Named format fields:
        >>> template = Template("My name is {name} and I am {age:d} years old")
        >>> template.parse("My name is John and I am 42 years old")
        {'name': 'John', 'age': 42}

        Indexed format fields:
        >>> template = Template("My name is {0} and I am {1:d} years old")
        >>> template.parse("My name is John and I am 42 years old")
        {0: 'John', 1: 42}

        Empty format fields:
        >>> template = Template("My name is {} and I am {:d} years old")
        >>> template.parse("My name is John and I am 42 years old")
        {0: 'John', 1: 42}

        Mixed format fields:
        >>> template = Template("My name is {} and I am {age:d} years old")
        >>> template.parse("My name is John and I am 42 years old")
        {0: 'John', 'age': 42}
        """
        data, span = _parse(self._fields, self._pattern, text)
        return data

    def search(self, item: Key, text: str) -> SearchResult:
        """Search text for item using template string

        Parameters
        ----------
        item : str or int
            Name or index of field
        text : str
            Text to search

        Returns
        -------
        value : Any
            Value of field
        span : tuple[int, int]
            Span of field in text

        Examples
        --------
        Named format fields:
        >>> template = Template("My name is {name} and I am {age:d} years old")
        >>> template.search("name", "My name is John and I am 42 years old")
        ('John', (11, 15))

        Indexed format fields:
        >>> template = Template("My name is {0} and I am {1:d} years old")
        >>> template.search(0, "My name is John and I am 42 years old")
        ('John', (11, 15))

        Empty format fields:
        >>> template = Template("My name is {} and I am {:d} years old")
        >>> template.search(0, "My name is John and I am 42 years old")
        ('John', (11, 15))

        Mixed format fields:
        >>> template = Template("My name is {} and I am {age:d} years old")
        >>> template.search(0, "My name is John and I am 42 years old")
        ('John', (11, 15))
        """
        return _search(self._fields, item, text)


def parse(template: str, text: str, ignore_case: bool = False) -> Result:
    """Parse text using template string

    Parameters
    ----------
    template : str
        Template string
    text : str
        Text to parse
    ignore_case : bool, optional
        Ignore case when matching fields, by default False

    Returns
    -------
    data : dict[str|int, Any]
        Parsed data as a dictionary

    See Also
    --------
    Template.parse: Parse text using the `Template` instance
    """
    return Template(template).parse(text)


def search(
    template: str, text: str, item: Key, ignore_case: bool = False
) -> SearchResult:
    """Search text for item using template string

    Parameters
    ----------
    template : str
        Template string
    text : str
        Text to search
    item : str or int
        Name or index of field
    ignore_case : bool, optional
        Ignore case when matching fields, by default False

    Returns
    -------
    value : Any
        Value of field
    span : tuple[int, int]
        Span of field in text

    See Also
    --------
    Template.search: Search text for item using the `Template` instance
    """
    return Template(template).search(item, text)


# noinspection PyShadowingBuiltins
def format(template: str, data: Result) -> str:
    """Format data using template string

    Parameters
    ----------
    template : str
        Template string
    data : dict[str|int, Any]
        Data to format

    Returns
    -------
    text : str
        Formatted text
    """
    return _format(template, data)
