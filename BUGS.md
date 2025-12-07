# BUGS.md

This document captures potential issues identified from a static review of the codebase as of this commit. No code was executed; findings are based on reading:

- run.py
- src/ui/main_window.py
- src/core/installer.py
- src/core/db_manager.py
- src/ui/stylesheet.py

Severity levels:

- Fatal: Security issues or crashes that block core functionality.
- Problematic: Likely to cause failures, data loss, or broken flows in common scenarios.
- Needs attention: Edge cases, portability, UX consistency, maintainability.
- Simple UI bugs: Minor polish issues.

## Priorities

1. Security & stability issues (**Fatal**).
2. Core installation correctness & data integrity (**Problematic**).
3. Portability & robustness across environments (**Needs attention**).
4. UX and visual polish (**Simple UI bugs**).

## Fatal

- Unsafe tar extraction (path traversal)
  - Location: `src/core/installer.py::extract_package()` uses `tar.extractall(path=...)` on untrusted archives without path normalization.
  - Impact: Malicious archives can write outside the temp dir (e.g., `../../etc/passwd`) leading to arbitrary file overwrite.
  - Suggestion: Implement a safe extract that rejects members whose normalized path escapes the target dir.
  - Status: Completed (fixed in code)

- SQLite connection used across threads
  - Location: `src/ui/main_window.py` creates a global `DBManager` on the GUI thread and passes it into `Worker` (QThread). `Installer.run_installation()` writes via that `DBManager` from the worker thread.
  - Impact: Python sqlite3 enforces `check_same_thread=True` by default → `ProgrammingError: SQLite objects created in a thread can only be used in that same thread` during/after install.
  - Suggestion: Create the DB connection inside the worker thread, or use separate connections per thread. If using `check_same_thread=False`, add proper locking.
  - Status: Completed (fixed in code)

- Python `setup.py install` ignores DESTDIR (installs into real system)
  - Location: `installer.run_installation()` for `build_system == 'python'` runs `python3 setup.py install` with `DESTDIR` env expecting staged install.
  - Impact: `setup.py install` generally ignores `DESTDIR` and may install into the live environment (or fail without root). Staging dir will be empty, tracking wrong.
  - Suggestion: Build wheels/SDist and install into a temp prefix (`pip install --root`/`--target`) or use virtualenv and record files.
  - Status: Completed (fixed in code)

## Problematic

- Naive root directory detection in archives
  - Location: `extract_package()` assumes first tar member’s top-level folder is the project root.
  - Impact: Archives with multiple top-level entries or unusual ordering will set `self.extracted_path` incorrectly → build system not detected.
  - Suggestion: Compute the common top-level prefix across members; if none, use the temp dir itself.
  - Status: Completed (fixed in code)

- Directory detection in UI based on trailing slash
  - Location: `src/ui/main_window.py::on_contents_item_clicked()` uses `member_name.endswith('/')` to detect directories.
  - Impact: Some tar members for directories may not end with `/`; misclassification causes odd UX.
  - Suggestion: Store `TarInfo.isdir()` alongside names when building the model, or encode a type role.
  - Status: Completed (fixed in code)

- Dependency flow leaves job in ambiguous state
  - Location: `Worker.run()` emits `dependency_found` without emitting `finished`.
  - Impact: The UI may appear mid-operation indefinitely with no clear completion state.
  - Suggestion: Emit a terminal state or support a resume path after user action.
  - Status: Completed (fixed in code)

- History item parsing is brittle
  - Location: `on_history_item_selected()` parses package name via `split(' ')[0]` from a label like `"name (version)"`.
  - Impact: Package names with spaces break lookup; multiple versions collapse to the first match.
  - Suggestion: Store package id/name/version in `QListWidgetItem` data roles instead of parsing strings; query by id.
  - Status: Completed (fixed in code)

- Installed files tracking portability
  - Location: `installer.run_installation()` collects installed files using `os.path` and prefixes with `/`.
  - Impact: On Windows backslashes may appear; DB may store mixed separators.
  - Suggestion: Normalize to POSIX-style paths for consistency.
  - Status: Completed (fixed in code)

- Duplicate app entry points
  - Location: `run.py` and `src/ui/main_window.py` both define a `__main__` block launching the app.
  - Impact: Confusion for contributors; risk of inconsistent execution paths.
  - Suggestion: Keep a single canonical entry script.
  - Status: Completed (fixed in code)

## Needs attention

- Extension handling
  - Locations: `dragEnterEvent` and `Installer.extract_package()` only accept `.tar.gz`, case-sensitive.
  - Impact: `.tgz` or uppercase extensions are rejected.
  - Suggestion: Case-insensitive check; support `.tgz`.

- Command availability and portability
  - Location: `installer.run_installation()` invokes `./configure`, `make`, `cmake`, `python3`.
  - Impact: Missing tools yield errors; `python3` might be `python` in some envs.
  - Suggestion: Preflight checks for required tools and adaptive Python invocation.

- Large file preview may freeze UI
  - Location: `read_file_from_archive()` used directly on click in the GUI thread.
  - Impact: Opening large/binary files blocks the UI.
  - Suggestion: Size/type check and lazy/async preview.

- Log growth unbounded
  - Location: `MainWindow.update_log()` appends indefinitely to `QTextEdit`.
  - Impact: Memory growth during long builds.
  - Suggestion: Cap lines, or stream to a file with a visible tail.

- DB concurrency and lifecycle
  - Location: DB reads from UI thread while writes from worker are planned.
  - Impact: Even with per-thread connections, missing commit/refresh strategies can cause stale reads.
  - Suggestion: Reload history after successful write; ensure clean shutdown (`DBManager.close`).

- Ambiguous package identity
  - Location: DB schema and `get_package_details(name)` selects by name only.
  - Impact: Multiple versions of the same package can’t be distinguished reliably.
  - Suggestion: Use package id in UI; allow multiple versions and filter accordingly.

## Simple UI bugs

- Multiple starts possible
  - Location: `start_installation()` doesn’t disable the button during an active run.
  - Impact: Users can start concurrent installs inadvertently.
  - Suggestion: Disable UI actions during install and re-enable on finish.

- No explicit feedback on bad drops
  - Location: `dragEnterEvent` rejects non-`.tar.gz` silently beyond ignore.
  - Impact: Users get no message why drop failed.
  - Suggestion: Show a status hint or toast.

- Archive contents tree usability
  - Location: `populate_contents_tree()` creates many flat nodes; no icons or type hints.
  - Impact: Hard to distinguish files vs dirs.
  - Suggestion: Add icons/roles; expand root node by default.

- Minor docs/consistency issues
  - `CONTRIBUTING.md` mentions “LibRARy” in places instead of “LibRARx”.
  - Typos like “Retrievels” in `DBManager.get_package_details` docstring (non-functional).

---

Notes:

- The application is intentionally Linux-focused (apt-based). On non-Linux or Windows, most build steps will not run; this is by design per README, but the app should fail gracefully with clear messages.
- Security fixes (tar safe extract) and threading fixes (SQLite per-thread) are the top priorities before release.
