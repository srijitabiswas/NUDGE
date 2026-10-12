# Intelligence / ML Environment Setup

## Requirements
- Python 3.13.3 or compatible Python 3
- No third-party packages currently required.

## Create the virtual environment
Run from the NUDGE repository root:
```powershell
python -m venv .venv
```

## Verify Python
```powershell
.\.venv\Scripts\python.exe --version
```

## Run tests
```powershell
.\.venv\Scripts\python.exe -m unittest discover -s ml -p "test_*.py" -v
```

All 23 current tests should pass.

## Notes
- .venv/ is excluded by the repository .gitignore.
- Current intelligence modules use Python standard-library functionality.
- Backend integration and testing with real project data remain outstanding.
