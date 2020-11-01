## Development

If you already cloned the repository and you know that you need to deep dive in the code, here are some guidelines to set up your environment.

## Use a virtual environment

You can use any virtual environment creator. I'll use virtualenv

```python
virtualenv env
```

### Active the environment

Activate the new environment with:


Linux/MacOS

```shell
source env/bin/activate
```

In windows

```shell
source ./env/Scripts/activate
```

## Install the dependencies

Note: _Install poetry first if you do not have yet for managing packaging and dependencies._

```python
poetry install
```

Then you can build the package by 

```python
poetry build
```

Note: _**Every time you install a new package with pip under that environment, activate the environment again.**_


