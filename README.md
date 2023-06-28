
```
            /$$       /$$$$$$$$                                         /$$$$$$$                             /$$   
           /$$/      | $$_____/                                        | $$__  $$                           |  $$  
          /$$/       | $$       /$$   /$$  /$$$$$$                     | $$  \ $$  /$$$$$$  /$$    /$$       \  $$ 
         /$$/        | $$$$$   |  $$ /$$/ /$$__  $$       /$$$$$$      | $$  | $$ /$$__  $$|  $$  /$$/        \  $$
        |  $$        | $$__/    \  $$$$/ | $$  \ $$      |______/      | $$  | $$| $$$$$$$$ \  $$/$$/          /$$/
         \  $$       | $$        >$$  $$ | $$  | $$                    | $$  | $$| $$_____/  \  $$$/          /$$/ 
          \  $$      | $$$$$$$$ /$$/\  $$|  $$$$$$/                    | $$$$$$$/|  $$$$$$$   \  $/          /$$/  
           \__/      |________/|__/  \__/ \______/                     |_______/  \_______/    \_/          |__/   
```

# Base Flask

## 1. Presentation and installation
### A - Prerequisite

For Windows, you needs :

* **Python 3.8.6** (or more)
* Relaunch **Shell prompt** (as administrator)

*WARNING !*
If you want to use the **HtmlToPdf** feature, you have ton install **wkhtmltopdf** on your OS : you can see this [here](https://pypi.org/project/pdfkit/) and specify the binary path in the .env file.

```python
python --version    # Verify version
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py
pip --version       # Verify version
pip install pipenv
```

### B - Clone the project

```bash
> git clone git@digitalcraft.fr:devs/boilerplate-flask-exo-dev.git
> cd boilerplate-flask-exo-dev
```

### C -  Create .env file and setup the config

### D - Launch SQL scripts on the DataBase

### E - Install and Launch the app

```bash
- pipenv --three (--python "3.8") # Création de l'env
- pipenv shell               # Activation
- pipenv install -d          # Installation des dépendances (eq. yarn install)
```

> Careful ! Pipfile isn't automatically update. Everytimes you add a new package, you've to update manually pipfile. Use the command `pip freeze` to show your packages actually installed.

```python
python run.py     # launch the app
```

## 2. Structure

### A - What's Base Flask ?

**Base Flask** (*boilerplate-flask-exo-dev*) is a Python's API Boilerplate used for projects who needs API's to call for managing datas (mainly with PostgreSQL as DBMS (*DataBase Management System*) or you can use MySQL/....)
<!-- @TODO: needs to update list and prepare for others DBMS -->

You can use any projects to call API's using REST (*REpresentational State Transfer*) calls :

* **Get** *(get one, or many, entities)*
* **Put** *(update datas of an entity)*
* **Post** *(create a new entity)*
* **Delete** *(delete an entity)*
* **Patch** *(update just some datas of an entity)*

The **Base Flask** is build using Blueprints, and can evolve easily by adding some new modules.

### B - Python's Modules

* **flask** : micro web Framework for Python.
* ***dev* flake8** : Runs all the tools by launching the single flake8 command. It displays the warnings in a per-file, merged output.
* ***dev* autotep8** : Automatically formats Python code to conform to the PEP 8 style guide. [Features to focus](https://pypi.org/project/autopep8/#features)
* **flask-cors** : A Flask extension for handling Cross Origin Resource Sharing (CORS), making cross-origin AJAX possible.
* **python-dotenv** : Reads the key-value pair from `.env` file and adds them to environment variable.
* **psycopg2-binary** : The most popular PostgreSQL database adapter.
* **mysql-connector-python** : The most popular MySQL database adapter.
* **flask-jwt-extended** : To create and use AccessToken.
* **webargs** : Parsing and validating HTTP request objects.
* **flask-sqlalchemy** : SQL Toolkit and Object Relational Mapper is a comprehensive set of tools for working with databases and Python specially with Flask.
* **flask-marshmallow** : ORM/ODM/framework-agnostic library for converting complex datatypes, such as objects, to and from native Python datatypes.
* **marshmallow-sqlalchemy** : bridge between the two plugins with some easy to use functions and process.
* **flask-swagger-ui** : Interface for Swagger-UI used to test routes and datas.
* **pdfkit** : Package used to generate PDF files from HTML templates.
* **loguru** : Loguru is a library which aims to bring enjoyable logging in Python.

## 1. Files

### A- Important Files

* `app/config.py` for import and add parameters for config the app
* `app/__init__.py` for the main code to launch the app
* `app/models.py` SQLAlchemy model for DB abstraction's classes
* `app/modules/*` for every modules of the app
* `app/utils/*` for using every methods/constants/enums/... of the app
* `tests` All tests to launch with *Pytest*

### B- Other folders/files

* `sql/*` SQL files for creating DB structure & first datas
* `app/core/*` for testing the status of the app
* `app/docs/*` Swagger interface for testing and documentation of API's calls
* `app/files/*` Files used by the application (py, images, pdf, csv...)
* `templates/*` Folder contains all HTML templates for PDF's files generation
* `generated_files/*` Folder contains all generated files from the application

## 2. Tests

`tests/endpoint_test.py` list all tests used and performed with the following command :

```python
pipenv shell
pytest
```

## 3. Delivery

There is no need to build the app, just clone it , init the virtual env, create the .env file and launch

```python
git clone git@XXXXXXXX
cd XXXXXXXX
pipenv --three
pipenv shell
pipenv install -d
# create .env file with the EXAMPLE one
nano .env
```

Same process of installation, but you can run the app on the background with this command :

```python
./launch.sh
```

The app will run on a screen named "exo-dev-api".

## 4. Technics information

<!-- @TODO: routes/token-auth/users/... -->
