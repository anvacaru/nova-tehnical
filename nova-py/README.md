# nova-py Project

This repository contains the source code for the nova-py project, managed using Poetry.

## Usage

Use Poetry to run the `nova-py` commands:

```bash
poetry run nova-py [COMMAND]
```

## Prerequisites

- **Python**: ^v3.11
- **make**: ^v3.81
- **Poetry**: [Poetry](https://python-poetry.org/) is a tool for dependency management and packaging in Python.

## Dependencies

Before you can start working with the project, you need to have Python and Poetry installed:

1. **Install Python**:
    - You can download and install Python from [python.org](https://www.python.org/downloads/).

2. **Install make and Poetry**:
    ```bash
    brew install poetry make
    ```

3. **Setup Project**:
    Once you have Poetry installed, run:
    ```bash
    make poetry-install
    ```

## Available Commands

You can use the following `make` commands:

- **poetry-install**: Install the project's dependencies.
    ```bash
    make poetry-install
    ```

- **format**: Automatically format your codebase.
    ```bash
    make format
    ```
