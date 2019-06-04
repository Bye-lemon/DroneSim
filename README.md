# DroneSim
3th Unmanned Aerial Vehicle Intelligent Sensing Technology Competition
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
#### Directory structure
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
├─docs
└─tests
```
## Usage
**Note: We are in the process of continuous development. When the development is completed, we will provide instructions on how to use it.**
## Authors
DLUT IoT Lab
## License
[MIT](https://tldrlegal.com/license/mit-license)