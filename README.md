# SmarTendance V1

## Information

- Python        : 3.12.3
- Docker Engine : WSLv2

## Setup & Installation

1. Build with Docker:

**Recommendation**: If you're using Windows, you can choose `Git Bash`.

```bash
docker-compose up --build
```

2. Build From Source

```bash
# Clone smartendance v1 repo
git clone https://github.com/wahyukiddies/Smartendance-Kel2.git

# Change directory to smartendance v1
cd web/

# Install python3-venv
sudo apt install -y python3-venv
# or you can install `virtualenv` module
sudo apt install -y virtualenv

# Create new virtualenv
python -m venv .venv

# Activate virtualenv
source .venv/Scripts/activate

# Installing requirements
pip install -r requirements.txt

# Database scheme migration
# MAKE SURE YOUR MySQL DATABASE SERVER IS RUNNING !
flask db init && flask db migrate -m "Initial db migration" && flask db upgrade

# Finally, you can running the app via wsgi.py file.
python wsgi.py
```
