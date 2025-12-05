# Contributing to LibRARx 🤝
Welcome! We are thrilled that you are interested in contributing to LibRARx, the Linux source code installation automation tool. Your contributions—whether code, documentation, bug reports, or feature suggestions—are vital to making this project better and safer for the entire Linux community.
This document outlines the guidelines for contributing to LibRARy.
## 🚀 How Can I Contribute?
There are many ways to contribute to LibRARy:
### 1. Reporting Bugs
Encountered a bug or unexpected behavior? Please report it!
 * Before Reporting: Check the existing [Issues](https://github.com/mNelty/targz-gui-projekt/issues) to ensure the bug hasn't already been reported.
 * Create an Issue: Use the Bug Report template provided (if available).
 * Include Details: Be as descriptive as possible. Include:
   * The version of LibRARx you used (if applicable).
   * Your Linux distribution (e.g., Ubuntu 22.04).
   * The exact steps to reproduce the bug.
   * Any error messages displayed in the GUI or terminal log.
### 2. Suggesting Features
We welcome ideas for improvement!
 * Create an Issue: Use the Feature Request template provided (if available).
 * Explain the Need: Clearly describe the proposed feature and why it would be valuable to LibRARx users. Focus on the problem the feature solves.
### 3. Writing Code
Ready to dive into the code? This is where your help makes the biggest impact.
Getting Started
 * Fork the Repository: Fork the official LibRARx repository to your GitHub account.
 * Clone the Fork: Clone your forked repository locally.
 
`git clone [https://github.com/](https://github.com/mNelty/targz-gui-projekt.git)`

`cd targz-gui-projekt`

 * Install Dependencies: Ensure you have the necessary Python dependencies installed (PyQt5).
   - `pip install PyQt5`

 * Create a New Branch: Always create a new, descriptive branch for your work.
   * For features: feat/new-feature-name
   * For bug fixes: fix/issue-number-bug-name
   
  e.g,  `git checkout -b feat/my-new-cli-command`

## Code Standards
 * Language: Python 3.8+ is required.
 * Styling: Follow PEP 8 standards strictly. Use a linter like flake8 or pylint to check your code.
 * Type Hinting: Use Python Type Hinting for all function arguments and return values.
 * Documentation: All new functions and classes must include clear docstrings (following the Google or NumPy style). Explain the purpose, arguments, and return values.
 * Modularity: Keep the separation of concerns:
   * src/core/: Core logic (Installer, DB management, system commands).
   * src/ui/: All PyQt GUI elements and presentation logic.
 * Testing: Whenever possible, include unit tests for new or modified core logic in src/core/.
## Submitting a Pull Request (PR)
 * Commit Often: Write clear, concise commit messages that explain what and why you made a change.
 * Pull Request: When your changes are complete:
   * Push your branch to your GitHub fork.
   * Open a Pull Request (PR) from your branch to the main LibRARy repository's main branch.
 * PR Description: Your PR description must clearly:
   * Reference any related Issues (e.g., Fixes #123 or Implements #456).
   * Explain the changes you made and the functionality added or fixed.
   * Include screenshots or GIF recordings for any changes to the GUI.
 * Review: A maintainer will review your code, provide feedback, and merge it once approved.
## 🏛️ Project Architecture Overview
LibRARx is designed with a clear separation between its logic and its presentation layers.
 * Installer (Core): Handles package extraction, build system detection, dependency error parsing (using regular expressions on stdout/stderr), and the secure DESTDIR installation method.
 * DB Manager (Core): Manages the SQLite database for tracking installed packages and every single file path associated with them.
 * UI/Worker Thread: The main GUI uses QThreads to offload the long-running installation and compilation tasks, ensuring the application remains responsive and the user interface never freezes.
Understanding this structure will help you target your contributions correctly.
Thank you for contributing to LibRARx!
