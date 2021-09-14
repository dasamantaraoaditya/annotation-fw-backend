# annotation-fw-backend

To setup the flask project follow the below steps:

## setup venv
#### Linux
sudo apt-get install python3-venv    # If needed
python3 -m venv env

#### macOS
python3 -m venv env

#### Windows
python -m venv env


## Open the project folder in VS Code

## Select python interpreter
In VS Code, open the Command Palette (View > Command Palette or (Ctrl+Shift+P)). Then select the Python: Select Interpreter command:
https://code.visualstudio.com/assets/docs/python/shared/command-palette.png

## Select the virtual environment to run
The command presents a list of available interpreters that VS Code can locate automatically (your list will vary; if you don't see the desired interpreter, see Configuring Python environments). From the list, select the virtual environment in your project folder that starts with ./env or .\env:
https://code.visualstudio.com/assets/docs/python/shared/select-virtual-environment.png

## Run the terminal
Run Terminal: Create New Integrated Terminal (Ctrl+Shift+`)) from the Command Palette, which creates a terminal and automatically activates the virtual environment by running its activation script.
https://code.visualstudio.com/assets/docs/python/shared/environment-in-status-bar.png

## update the pip venv (optional)
Update pip in the virtual environment by running the following command in the VS Code Terminal:

-> python -m pip install --upgrade pip

## Install flask
Install Flask in the virtual environment by running the following command in the VS Code Terminal:

-> python -m pip install flask

## Install flask_mysqldb
Install Flask in the virtual environment by running the following command in the VS Code Terminal:

-> python -m pip install flask_mysqldb

## Run the application
Run the flask application with following commnad :

-> python -m flask run

## configurations
This would run the flask backend on localhost:5000

### Database
mysql data base has been used to store data and images are stored in project folder, below are the configuration for a free hosting mysql server

app.config['MYSQL_HOST'] = 'sql6.freemysqlhosting.net'
app.config['MYSQL_USER'] = 'sql6436112'
app.config['MYSQL_PASSWORD'] = 'dxQH1qb931'
app.config['MYSQL_DB'] = 'sql6436112'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
