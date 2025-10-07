# chill_app
Chill Study App

## Prerequisites
- Python 3.11 (recommended for all contributors)
- Git

### Install Python 3.11
- macOS (Homebrew):
  ```bash
  brew install python@3.11
  echo 'export PATH="/opt/homebrew/opt/python@3.11/bin:$PATH"' >> ~/.zshrc
  exec zsh
  python3.11 --version
  ```
- Windows:
  - Install Python 3.11 from the official installer (`https://www.python.org/downloads/windows/`) and check "Add python.exe to PATH" during setup.
  - Verify:
    ```bat
    py -3.11 --version
    ```
- Linux (Debian/Ubuntu):
  ```bash
  sudo apt update
  sudo apt install -y python3.11 python3.11-venv python3.11-distutils
  python3.11 --version
  ```

## Getting the code
1. Set up Git with your name and email (first time only):
   ```bash
   git config --global user.name "Your Name"
   git config --global user.email "you@example.com"
   ```
2. Clone the repository:
   ```bash
   git clone git@github.com:Table-Titans/chill_app.git
   cd chill_app
   ```
   - If you prefer HTTPS:
     ```bash
     git clone https://github.com/Table-Titans/chill_app.git
     cd chill_app
     ```
3. Ensure you are on the main branch and up to date:
   ```bash
   git checkout main
   git pull
   ```

## Create and activate a virtual environment (Python 3.11)
- macOS/Linux:
  ```bash
  python3.11 -m venv .venv
  . .venv/bin/activate
  ```
- Windows (PowerShell or CMD):
  ```bat
  py -3.11 -m venv .venv
  .\.venv\Scripts\activate
  ```

## Install dependencies
Upgrade tooling, then install pinned requirements:
```bash
python -m pip install -U pip setuptools wheel
pip install -r requirements.txt
```

## Running the app
- Using the `python` entrypoint:
  ```bash
  python app.py
  ```
  The app will start in debug mode at `http://127.0.0.1:5000/`.

- Or using Flask CLI:
  ```bash
  export FLASK_APP=app:app     # Windows PowerShell: $env:FLASK_APP = "app:app"
  export FLASK_DEBUG=1         # Windows PowerShell: $env:FLASK_DEBUG = "1"
  flask run
  ```

## Project structure
```
app.py                 # App entrypoint (creates app via src.create_app)
src/__init__.py        # App factory & bootstrap init
src/routes.py          # Routes blueprint
src/templates/         # Jinja templates
src/static/            # Static resources like images, css files, or js files
requirements.txt       # Pinned dependencies
```

## Troubleshooting
- If `pip install -r requirements.txt` fails due to NumPy on Python 3.12, ensure you are using Python 3.11 or upgrade NumPy to a compatible version (`1.26.4`).
- If `flask` is not found, ensure the virtual environment is activated and dependencies are installed.
- On Windows, if activation is blocked, enable scripts:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```
- If port 5000 is in use, set a different port:
  ```bash
  flask run --port 5050
  ```

## Common Git commands
```bash
# Create a new branch
git checkout -b feature/short-description

# Commit and push
git add -A
git commit -m "Describe your change"
git push -u origin HEAD

# Update your branch with main
git fetch origin
git merge origin/main
```