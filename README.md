# DroneSim
[![Documentation Status](https://readthedocs.org/projects/dronesim/badge/?version=latest)](https://dronesim.readthedocs.io/en/latest/?badge=latest) [![Build Status](https://travis-ci.org/Bye-lemon/DroneSim.svg?branch=master)](https://travis-ci.org/Bye-lemon/DroneSim) [![codebeat badge](https://codebeat.co/badges/cf840276-6fd2-45e9-b01a-bf48d45ef35e)](https://codebeat.co/projects/github-com-bye-lemon-dronesim-master) ![PyPI](https://img.shields.io/pypi/v/DroneSim.svg) ![PyPI - Format](https://img.shields.io/pypi/format/DroneSim.svg) ![GitHub](https://img.shields.io/github/license/Bye-lemon/DroneSim.svg)<br>
3th Unmanned Aerial Vehicle Intelligent Sensing Technology Competition
## Docker
**Note: We are in the process of continuous development. When the development is completed, we will provide instructions on how to use it.**
## Usage
**Note: We are in the process of continuous development. When the development is completed, we will provide instructions on how to use it.**
## Development
#### Environment
Before you start developing, you'd better create an independent working environment.
```bash
python -m venv .
```
You can activate the virtual environment using the following commands. All your development processes should be in this virtual environment.
```bash
# For Linux
source ./bin/activate

# For Windows
Scripts\activate.bat
```
After activate virtual environment, install all the necessary dependencies.
```bash
pip install -r requirements.txt
```
#### Directory Structure
```text
DroneSim:
.
│  .gitignore
│  LICENSE
│  README.md
│  requirements.txt
│  setup.py
├─app
│  │  main.py
│  ├─config
│  ├─driver
│  ├─task
│  ├─utils
│  └─vision
├─bin
├─docs
├─pack
└─tests
```
#### API Docs
View [https://dronesim.readthedocs.io/en/latest/](https://dronesim.readthedocs.io/en/latest/)
## Authors
DLUT IoT Lab
## License
[MIT](https://tldrlegal.com/license/mit-license)
