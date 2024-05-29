Some(value), Maybe(None)

A simple Option type for Python 3 inspired by Rust, fully type annotated.

Installation
============

Latest GitHub master branch version:

$ pip install git+https://github.com/mbalzert1978/option

Summary
=======

The idea is that a option can be either Some(value) or Maybe(None), with a way to differentiate between the two. Some and Maybe are both classes encapsulating an arbitrary value.

API
===

Creating an instance:
``` python
>>> from option import Some, Maybe
>>> value = Some(42)
>>> no_value = Maybe(None)
# Checking whether a result is Some or Maybe:

>>> value.is_some()
True
>>> no_value.is_none()
True

# Accessing the Value:

>>> unwrapped = value.unwrap()
42
# This will raise an exception:
unwrapped = no_value.unwrap()

# Handling the Absence of Value:

>>> unwrapped = value.unwrap_or(0)
42
default_value = no_value.unwrap_or(0)
0

# Mapping and Transforming Values:

>>> transformed = value.map(lambda x: x * 2)
Some(84)
# Mapping a Maybe does nothing:
transformed = no_value.map(lambda x: x * 2)
Maybe(None)
```

Contributing

Contributions to option are welcome. You can find the source code on GitHub and submit pull requests.

License

option is available under the MIT License.
