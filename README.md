# fTmplt

> Simple string parsing and formatting using Python's format strings


## Install

```shell
pip install git+https://github.com/dylanljones/ftmplt.git
```


## Usage

### Parse

```python
>>> import ftmplt
>>> template = "Hello, my name is {name} and I am {age:d} years old."
>>> string = "Hello, my name is John and I am 42 years old."

>>> ftmplt.parse(template, string)
{'name': 'John', 'age': 42}
```

### Search

```python
>>> import ftmplt
>>> template = "Hello, my name is {name} and I am {age:d} years old."
>>> string = "Hello, my name is John and I am 42 years old."

>>> ftmplt.search(template, string, "name")
('John', (19, 23))

>>> ftmplt.search(template, string, "age")
(42, (33, 35))
```

### The template object

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