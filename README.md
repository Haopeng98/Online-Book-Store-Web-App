# *Sahara*

### Introduction

Sahara is an online Bookstore web app written for UGA's CSCI 4050 (Software Engineering) class.

A lot of inspiration for the structure of this project was taken from Corey Schafer's series on
Flask, which I would also recommend for getting introduced to the framework
([link](https://www.youtube.com/playlist?list=PL-osiE80TeTs4UjLw5MM6OjgkjFeUxCYH)).

This application uses the MVC pattern, where the models are defined in the `sahara/models.py` file
as connections to the data of the app, views are defined in the `sahara/templates/` directory as
templated html rendered dynamically based on data from the models, and the controller is the Flask
app itself, extended by the function callbacks defined in `sahara/routes.py` file, where the
controller calls on the models and views mentioned above to marshal a response to an HTTP request.

### Getting Started

#### *System Requirements*

* Git ([Download link](https://git-scm.com/downloads))
* Python v3.9+ ([Download link](https://www.python.org/downloads/))
* Some database software (MySQL, sqlite3, etc)
    * Possibly some python modules to interface with said software, explained later on.

This app was developed using Python version 3.9, so I recommend using version 3.9 or newer. Slightly
older versions will probably work fine, but I can't guarantee that beacause I haven't tested it.

#### *Installation*

This application requires database software to function. I recommend using sqlite3 for developpment,
but MySQL will be used in the context of deploying this application. These next steps will focus on
getting sqlite3 ready for use, since it is the easier and smaller of the two options.

Start by seeing if sqlite3 is already installed on your system.

```  txt
[Command Prompt/Powershell]
sqlite3.exe

[Mac/Linux]
sqlite3
```

This command should open the sqlite3 prompt if it is installed on your system. If you don't have
sqlite3 installed, I recomment using
[this guide](https://www.tutorialspoint.com/sqlite/sqlite_installation.htm) to install it. After
the installation, make sure that you can start sqlite3 using the commands above.

Now for this application.

Start by running the following command in Powershell/Command Prompt on Windows, the Terminal app on
Mac, or your favorite terminal emulator on Linux.

``` txt
[Any]
git clone https://github.com/calebrjc/Sahara.git
```

Then, navigate to the Sahara folder that was created.

*NOTE: For any commands written in this README, I'll assume that your Python executable is on your
system's PATH and can be run from your shell of choice using the `python` command. If not, you'll
need to either add the executable to your PATH or change the command to fit your setup.*

*To see if Python is on your system's PATH, try opening your shell and typing `python --version`.
If it works, you're all good! Else, add the executable to your system's PATH.*

First, we'll create a virtual environment for this app.

``` txt
[Any]
python -m venv env
```

Then, we'll activate that environment so that our next commands only effect this local environment.

```  txt
[Command Prompt]
.\env\Scripts\activate

[Powershell]
.\env\Scripts\Activate.ps1

[Mac/Linux]
source env/bin/activate
```

*NOTE: Installing the following before moving on should help you avoid a lot of errors that may come
up during the requirements installation process.*
``` txt
[Any]
pip install wheel
```

Next, we'll install the required modules, listed in the `requirements.txt` file.

``` txt
[Any]
pip install -r requirements.txt
```

*NOTE: Some database softwares need extra modules to work with this application.
For instance, if you're using MySQL, you'll have to install the `mysqlclient` module separately.*
``` txt
[Any]
pip install mysqlclient
```

This application will read some configuration data from a file in the workspace root directory
called `.env`. Please rename the `sample_env.env` file to `.env` and make the necessary changes to
it. For example, if you're using sqlite3:

``` txt
[Sahara/.env]

DATABASE_URI = "sqlite:///site.db"
MAIL_SERVER = "smtp.googlemail.com"
MAIL_PORT = "587"
MAIL_USE_TLS = "True"
EMAIL_USER = [check Discord]
EMAIL_PASS = [check Discord]
```

Next, we'll run the setup script located in the home directory.

``` txt
[Any]
python setup.py
```

If you're using the configuration above, you should see a new file in the `Sahara` folder named
`site.db`.

Finally, we'll leave the virtual environment.

``` txt
[Any]
deactivate
```


### Execution

To run this program...

First, activate your virtual environment.

``` txt
[Command Prompt]
.\env\Scripts\activate

[Powershell]
.\env\Scripts\Activate.ps1

[Mac/Linux]
source env/bin/activate
```

Then, run the run.py script in the project root.

``` txt
[Any]
python run.py
```

Don't forget to deactivate the virtual environment when you don't need it anymore.

``` txt
[Any]
deactivate
```
