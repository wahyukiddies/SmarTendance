# Smartendance V1

## Development Environment

- Operating System  : Windows 11
- Python version    : 3.12.3
- Docker Engine     : Kali Linux WSLv2

## Setup & Installation

- **Clone Smartendance Repo's**:

```bash
git clone https://github.com/wahyukiddies/Smartendance-Kel2.git
```

- **Build with Docker**:

**Recommendation**: If you're using Windows, you can use `Git Bash`.

```bash
docker-compose up -d --build
```

- **Build From Source**:

```bash
# Change directory to smartendance v1
cd web/

# Install python3-venv
sudo apt install -y python3-venv
# or you can install `virtualenv` module
sudo apt install -y virtualenv

# Create new virtualenv
py -m venv .venv

# Activate virtualenv
source .venv/Scripts/activate

# Installing requirements
pip install -r requirements.txt

# Database scheme migration
# MAKE SURE YOUR MySQL DATABASE SERVER IS RUNNING !
flask db init && flask db migrate -m "Initial db migration" && flask db upgrade

# Finally, you can running the app via wsgi.py file.
py wsgi.py # Windows
python3 wsgi.py # Linux/Mac
```
