# Contributing to Copyright-Free Image Viewer

First off, thank you for considering contributing to `copyright-free-image-viewer`! We welcome contributions from everyone—whether it's adding a new feature, fixing a UI bug, or improving the documentation.

## Getting Started

1. **Fork & Clone:** Fork the repository on GitHub and clone it to your local machine.
2. **Environment:** Ensure you have Python 3.9+ and optionally Docker installed.
3. **Installation:** We recommend setting up a virtual environment.
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
4. **Pre-commit Hooks:** We use `pre-commit` to ensure code quality and formatting via `ruff`. Install the hooks in your local repository:
   ```bash
   pre-commit install
   ```

## Development Workflow

1. **Branching:** Create a new branch for your feature or bug fix:
   ```bash
   git checkout -b feature/my-awesome-feature
   ```
2. **Making Changes:** Make your changes in the respective directories (`routes/`, `templates/`, `services/`).
   - Note: The core API fetching logic is managed by the `stock-fetcher` package. If you need to add a new image provider, please contribute to the `stock-fetcher` repository directly!
3. **Committing:** Commit your changes. `pre-commit` will automatically run Ruff to format and lint your code. If the checks fail, fix the issues and stage/commit again.

## Pull Requests

- Keep your pull requests focused on a single issue or feature.
- Provide a clear, detailed description of the problem you are solving and how you approached the solution.
- If your PR introduces a breaking change (e.g., modifying the SQLite database schema), please highlight it explicitly and provide database migration instructions if applicable.

Thank you for helping us make this viewer better!
