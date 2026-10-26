# Reproduce the Python environment — macOS arm64 / CPython 3.12

Validated October 26, 2026 with CPython **3.12.14**, existing Python distribution, and product source `cad0604e477d15edc437d38057b26f78057938e8`. [Evidence](../reports/baseline/V1_REBUILD_EVIDENCE.json) · [Closeout boundaries](V1_BOUNDED_CLOSEOUT.md).

## Fixed artifacts and provenance

[v1-macos-arm64-py312.lock](../requirements/v1-macos-arm64-py312.lock) pins all 46 resolved wheels by version and SHA-256, including selected extras and build tools: pip 25.1.1, setuptools 84.2.1 and wheel 0.48.0. Runtime dependencies were resolved against the existing environment's observed versions, using the configured pip package source; pip/setuptools/wheel are included explicitly. Private resolution logs and wheel inventory retain provenance. The hashes identify the selected wheel artifacts, not every distribution of each package. Marker/platform alternatives were not resolved for other targets; do not call this a cross-platform lock.

This lock does not pin/download the Python interpreter or operating system, install LM Studio or models, or authenticate Google. The original `requirements-dev.txt` is a historical snapshot. Existing unpinned CI/setup instructions remain baseline workflows; only the procedure here tests the hash-fixed environment.

## Procedure in a separate checkout/environment

Use an arm64 CPython 3.12 interpreter (the recorded patch version for closest reproduction). Start from the reviewed source commit. Choose **new** directories; never reuse/delete the existing `.venv` or previous evidence. The variables below are examples to replace with new paths.

```sh
REBUILD_ROOT=/absolute/new/private/rebuild-directory
mkdir -m 700 "$REBUILD_ROOT"
python3.12 -m venv "$REBUILD_ROOT/clean"
"$REBUILD_ROOT/clean/bin/python" -m pip download \
  --require-hashes --only-binary=:all: \
  -r requirements/v1-macos-arm64-py312.lock \
  --dest "$REBUILD_ROOT/wheelhouse"
"$REBUILD_ROOT/clean/bin/python" -m pip install \
  --no-index --find-links "$REBUILD_ROOT/wheelhouse" \
  --require-hashes --only-binary=:all: \
  -r requirements/v1-macos-arm64-py312.lock
"$REBUILD_ROOT/clean/bin/python" -m pip wheel \
  --no-index --no-build-isolation --no-deps \
  --wheel-dir "$REBUILD_ROOT/project-wheel" .
"$REBUILD_ROOT/clean/bin/python" -m pip install \
  --no-index --no-deps "$REBUILD_ROOT"/project-wheel/*.whl
"$REBUILD_ROOT/clean/bin/python" -m pip check
"$REBUILD_ROOT/clean/bin/python" -I -c \
  'import mcp, requests, google_auth_oauthlib, harness.calendar_agent'
"$REBUILD_ROOT/clean/bin/python" -m pytest -q -ra
```

Network is required for the download step only; install/build use the wheelhouse and already pinned build tooling. No model/Google call is needed. Keep the venv executable path itself: resolving its symlink can bypass the environment. Also test installed-wheel imports from a directory outside the checkout; pytest intentionally imports `src/` and by itself does not prove wheel installation.

For evidence, save the source commit and hashes, Python/platform/package inventory, download logs, lock/wheel SHA-256, `pip check`, imports and complete pytest output. The actual run also installed the project wheel using its recorded hash and compared packaged Python bytes to the source. Wheel build timestamps can differ; this does not claim bit-for-bit reproducible wheel builds. Keep installer logs/paths private and owner-only; publish only reviewed metadata. A new Python environment on the same Mac does not establish a new-machine, runtime/model or OAuth recreation.
