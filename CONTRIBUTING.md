# Contributing to PyATS Read-Only API

First off, thank you for considering contributing to this project! It's people like you that make open source tools great.

This project aims to provide a secure, professional-grade API for network automation, and we welcome help with bug fixes, documentation improvements, and feature enhancements.

## Getting Started

1.  **Fork the repository** on GitHub.
2.  **Clone your fork** locally:
    ```bash
    git clone [https://github.com/YOUR-USERNAME/pyats-ro-api.git](https://github.com/YOUR-USERNAME/pyats-ro-api.git)
    cd pyats-ro-api
    ```
3.  **Create a branch** for your specific changes. We recommend using `feat/` for features or `fix/` for bugs:
    ```bash
    git checkout -b feat/add-junos-support
    ```

## Development Environment

We have automated the setup process using Docker and Make to ensure consistency.

* **Start the dev environment:**
    ```bash
    make dev
    ```
    This spins up the containers with hot-reloading enabled.

* **Run the specific services (REST API vs MCP):**
    See the `README.md` for specific `docker-compose` commands if you only need one service.

## Testing & Quality

Your code must pass all tests before we can merge it.

1.  **Run the test suite:**
    ```bash
    make test
    ```
2.  **Lint your code:**
    Please ensure your code follows standard Python formatting (Black/PEP8).
    ```bash
    # If running locally
    black app/ tests/
    flake8 app/
    ```
3.  **Add new tests:**
    If you add a feature, please add a corresponding test case in `tests/`.
    If you fix a bug, please add a test that reproduces the bug to ensure it doesn't return.

## Submitting a Pull Request (PR)

1.  Push your branch to your fork.
2.  Open a Pull Request against the `main` branch.
   > **Note**: Currently, all PRs target `main`. A `develop` branch strategy is planned for future releases (see [DEVELOPMENT_ROADMAP.md](DEVELOPMENT_ROADMAP.md) for details).
3.  Fill out the **Pull Request Template** completely.
4.  Wait for the automated CI checks to pass.
5.  I (or a maintainer) will review your code. We might suggest changes—this is a normal part of the process!

## Security Guidelines

Since this tool interacts with network infrastructure:
* **Never commit credentials.**
* **Maintain Read-Only status:** Ensure any new command execution logic maintains the "read-only" constraint.
* **Input Sanitization:** If you touch command parsing, ensure you use the existing sanitization methods to prevent command injection.

## Code of Conduct

Please be respectful and professional in all issues and pull request comments.