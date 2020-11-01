## Development

If you already cloned the repository and you know that you need to deep dive in the code, here are some guidelines to set up your environment.

## Use a virtual environment

You can use any virtual environment creator. I'll use virtualenv in this example.

```python
virtualenv env
```

## Active the environment

Activate the new environment with:


Linux/MacOS

```shell
source env/bin/activate
```

In windows

```shell
source ./env/Scripts/activate
```

## Installing dependencies

```python
pip install -r requirements/dev.txt
```

## Testing the package

Note: _Install poetry first if you do not have yet for managing packaging and dependencies._

```python
poetry install
```

Then you can build the package by 

```python
poetry build
```

Note: _**Every time you install a new package with pip under that environment, activate the environment again.**_


## Opening a PR.

* Make sure you have formatted your files and used static-typing.

We use MyPy for type checking, you can check you have annotted correctly with:

```python
./scripts/type_test.sh

Success: no issues found in 15 source files
```

For formatting we use isort and black, you can run them by:

```python
./scripts/format.sh

All done! ✨ 🍰 ✨
3 files reformatted, 12 files left unchanged.
```
