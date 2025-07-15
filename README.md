# asa

Opinionated CLI for [Asana](https://asana.com/).

## Getting started

> **Prerequisites**
> 
> * [just](https://just.systems/man/en/) - task runner.
> * [uv](https://docs.astral.sh/uv/) - Python package/project manager.

1. Install dependencies:

```sh
just init
```

2. Run the application:

```sh
just run
```

## Building

> **Prerequisites**
> 
> * [pipx](https://pipx.pypa.io/latest/)

To build and install the app:

```sh
just build
```

Now, assuming that `pipx` is configured to install to somewhere on your `PATH`, the `asa` executable should be available.