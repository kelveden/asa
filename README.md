# asa

Opinionated CLI for [Asana](https://asana.com/).

## Getting started

> **Prerequisites**
> 
> * [just](https://just.systems/man/en/) - task runner.
> * [uv](https://docs.astral.sh/uv/) - Python package/project manager.

1. Install the dependencies:

```sh
just init
```

2. Now either:

* [Install and run the `asa` binary](#installing-the-asa-binary); or
* [Run asa from source](#running-from-source)

## Installing the `asa` binary

> **Prerequisites**
> 
> * [pipx](https://pipx.pypa.io/latest/) - Make sure [that it is configured to install binaries](https://github.com/pypa/pipx/blob/main/docs/installation.md#installation-options) to a location on your `PATH`.

To install the app as a binary:

```sh
just install
```

Now, run the app:

```sh
asa
```

## Running from source

To run the application directly from source code (useful for development):

```sh
just run
```

e.g.

```sh
just run --help
```
