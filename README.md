# asa

Opinionated CLI for [Asana](https://asana.com/).

## Getting started

> **Prerequisites**
> 
> * [just](https://just.systems/man/en/) - task runner.
> * [uv](https://docs.astral.sh/uv/) - Python package/project manager.

1. Install the dependencies and pre-commit hook:

```sh
just init
```

2. Now either:

* [Install and run the `asa` binary](#installing-and-running-the-asa-executable); or
* [Run asa from source](#running-from-source)

## Installing and running the `asa` executable

To install the app as a binary:

```sh
just install
```

Now, create the initial configuration:

```sh
asa config --init
```

The `asa` executable is now ready to use.


## Running from source

To run the application directly from source code (useful for development):

```sh
just run <asa command>
```

> [!tip]
> Just like when [running the `asa` executable](#installing-and-running-the-asa-executable), you will
> need to ensure that a valid config file exists at `~/.config/asa/config.ini` - run: `just run config --init`
> to generate a new config file.
