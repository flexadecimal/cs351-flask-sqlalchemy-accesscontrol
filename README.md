# CS351 authentication demo

## Installation
1. Install requirements through apt, python > 3.8 (requires dataclasses for user serialization)
```
sudo apt install python3 python3-pip python3-flask
```
2. Install python package requirements.
```
python3 -m pip install -r requirements.txt
```
3. Make `scripts` executable.
```
chmod -R u+r+x ./scripts
```
4. Run `setup_tables.py` to create tables.
```
python3 ./scripts/setup_tables.py
```
5. Run flask app (from top level directory!)
```
./scripts/run.sh
```
