# fTmplt

> Simple string parsing and formatting using Python's format strings

This project is similar to [parse], but emphasizes on format strings that are both
parsable and formattable. This means only format specifiers that are both valid
for parsing and formatting are supported. It was originally developed to parse and format
input and output files for various computational physics libraries.


## Installation

```shell
pip install git+https://github.com/dylanljones/ftmplt.git
```

## Format Specification

The full ``format()`` [Format Specification Mini-Language][format-spec] with all types
is supported:

> [[fill]align][sign][0][width][.precision][type]

| Type | Description                               | Output    |
|:-----|:------------------------------------------|:----------|
| None | Unformatted strings                       | ``str``   |
| d    | Decimal integer                           | ``int``   |
| b    | Binary integer                            | ``int``   |
| o    | Octal integer                             | ``int``   |
| x    | Hex integer                               | ``int``   |
| f    | Fixed point floating point                | ``float`` |
| e    | Floating-point numbers with exponent      | ``float`` |
| g    | General number format (either d, f or e)  | ``float`` |
| %    | Percentage                                | ``float`` |

Additionally, ``datetime`` objects can be parsed and formatted using the ``strftime()``
[Format Codes][datetime-spec].

The differences between ``parse()`` and ``format()`` are:

- The align operators will cause spaces (or specified fill character) to be stripped
  from the parsed value. The width is not enforced; it just indicates there may be
  whitespace or "0"s to strip.
- Numeric parsing will automatically handle a "0b", "0o" or "0x" prefix.
  That is, the "#" format character is handled automatically by d, b, o and x formats.
  For "d" any will be accepted, but for the others the correct prefix must be present if at all.
- The "e" and "g" types are case-insensitive so there is not need for the "E" or "G" types.
  The "e" type handles Fortran formatted numbers (no leading 0 before the decimal point).


## Usage

Define a template using the Python format string syntax.
From there it's a simple thing to parse, search or format a string.
```python
>>> import ftmplt
>>> template = "Hello, my name is {name} and I am {age:d} years old."
>>> string = "Hello, my name is John and I am 42 years old."
```

Parse all parameters from a string:
```python
>>> ftmplt.parse(template, string)
{'name': 'John', 'age': 42}
```
or search a string for some pattern:
```python
>>> ftmplt.search(template, string, "name")
('John', (19, 23))

>>> ftmplt.search(template, string, "age")
(42, (33, 35))
```

### The template object

If you're going to use the same pattern to match lots of strings you can use the
``Template`` object. Once initialised, the template object can be used similarly
to the functions above:

```python
>>> import ftmplt
>>> template = ftmplt.Template("Hello, my name is {name} and I am {age:d} years old.")
>>> string = "Hello, my name is John and I am 42 years old."

>>> template.parse(string)
{'name': 'John', 'age': 42}

>>> template.search("name", string)
('John', (19, 23))

>>> template.format({"name": "John", "age": 42})
"Hello, my name is John and I am 42 years old."
```

### Example: Parsing a file

Let's say you have a file ``data.txt`` with a bunch of parameters in it:
```text
Input-File
N=50 M=100
X=1.0 Y=2.0 Z=3.0
Output-Text:
Some multi-line
output text to the end of the file
```

You can handle the file formatting and parsing with a template:
```python
from pathlib import Path
import ftmplt

template = ftmplt.Template("""
Input-File
N={n:d} M={m:d}
X={x:.1f} Y={y:.1f} Z={z:.f}
Output-Text:
{output}
""")

file = Path("data.txt")
# Read file and parse data
data = template.parse(file.read_text())
# Update values
data["n"] = 100
...
# Update file contents
file.write_text(template.format(data))
```

[parse]: https://github.com/r1chardj0n3s/parse
[format-spec]: https://docs.python.org/3/library/string.html#format-specification-mini-language
[datetime-spec]: https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
