# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Pretty Logger is a Python logging utility library built on `coloredlogs` and the standard `logging` module. It provides colored, text-wrapped console output, file logging, and per-module logger configuration.

## Build & Install

```bash
poetry install          # Install all dependencies
poetry build            # Build the package
```

Python >= 3.11 required. Uses Poetry with src layout (`src/pretty_logger/`).

## Type Checking

```bash
mypy src/
```

The package is PEP 561 compliant (`py.typed` marker + `.pyi` stubs).

## Architecture

The library exposes two main entry points from `src/pretty_logger/pretty_logger.py`:

- **`configure_pretty_logging()`** — Configures the root logger with file + console handlers, color formatting, text wrapping, and silences noisy third-party modules (pymongo, motor, httpcore, httpx, pdfminer, openai, python_multipart). Guards against duplicate handler attachment.
- **`get_module_logger()`** — Creates named loggers for individual modules with optional independent log files. Can inherit from root or run standalone.

Key internal classes:
- **`EnsureClassName`** (logging.Filter) — Guarantees every log record has a `className` attribute.
- **`WrappedColoredFormatter`** (logging.Formatter) — Wraps a `ColoredFormatter` with configurable line-width wrapping while preserving empty lines.

Helper: `get_git_root()` retrieves the git repo root for path-based log file placement.

## Log Format

```
[%(asctime)s.%(msecs)03d] - %(name)s - %(levelname)s - %(filename)s:%(lineno)d [%(funcName)s]: %(message)s
```

Default log path: `logs/pretty_logger.log`. Times are converted to GMT.
