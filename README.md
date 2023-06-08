# fTmplt

> Simple string parsing and formatting using Python's format strings

This project is similar to [fparse](https://github.com/catalystneuro/fparse), but
improves parsing and formatting. It was originally developed to parse and format
input and output files for various computational physics libraries.

Parse strings using a specification based on the Python format() syntax.
> ``parse()`` is the opposite of ``format()``


## Installation

```shell
pip install git+ssh://git@github.com/dylanljones/ftmplt.git
```


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
