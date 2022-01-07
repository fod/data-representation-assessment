# data-representation-project
## Food Logger

### Contents
1. [Overview](#overview)
1. [Running the application](#running-the-application)
1. [Using the application](using-the-application)
1. [Deployment](deployment)

### Overview
Food Logger is a demonstration CRUD web application built with Python and Flask. A live demo of the application is available at https://www.data-representation-project.eu. This document provides a description of the application and its features, as well as instructions on how it might be downloaded and run locally.

### Running the application
This application was developed on a Linux system but has been tested on both Linux and Windows. To run the application on a user's own machine the following steps should be followed. Note that on Windows it is assumed that [cmdr](https://cmder.net/) or similar is installed.

These steps assume that [Git](https://git-scm.com/), [mysql-shell](https://dev.mysql.com/downloads/shell/) or similar, [Python](https://www.python.org/) and [pip](https://pypi.org/project/pip/) are installed and that a local [MySQL server](https://dev.mysql.com/downloads/mysql/) is running within which the user has the appropriate privileges to run the necessary commands.

1. Clone this repository with ```git clone git@github.com:fod/data-representation-project.git```
1. Enter repository directory: ```cd data-representation-project```.
1.  Create a Python virtual environment: ```python -m venv .venv```.
1. Activate the virtual environment: ```source .venv/bin/activate``` or, on Windows: ```.venv\Scripts\activate.bat```.
1. Install the required modules: ```pip install -r requirements.txt```
1. Initialise and populate application database: ```mysql -u [USERNAME] -p < db/initDB.sql```. Note that on Windows mysql must be on the Windows ```PATH```, otherwise it must be invoked using the full path to the mysql executable; e.g. ```"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u USER -p < db\initDB.sql```

1. Edit ```settings.py``` to reflect local settings; specifically:
    - ```EDAMAM_APP_ID``` and ```EDAMAM_API_KEY``` are the app id and api key used by this application to access the [Edamam Food Database API](https://developer.edamam.com/food-database-api-docs). To avoid harvesting by bots, these cannot be included in the repository. Instead they are available at https://gist.github.com/fod/7437a5931192c295d37dd532d8b01176. The shorter code ending with '```ddd```' is the APP_ID and the longer one, ending with '```5af```' is the API_KEY. Alternatively, the user can sign up for their own ID and key at the [EDAMAM API website](https://developer.edamam.com/).
    - ```MYSQL_HOST``` should equal ```localhost``` if using a local database, 
    - ```MYSQL_USER``` should be the username of a user who has access to the ```food``` database. This will probably be the user used to initialise and populate the database or a default application user.
    - ```MYSQL_PASSWORD``` should be that user's password.
    - ```SECRET_KEY``` is the Flask secret key. It should be a string of random bytes but leaving it as it is will work fine too.


1. Start the Flask development server with ```sh start.sh``` and browse to [http://127.0.0.1:5000](http://127.0.0.1:5000) to use the app.


### Using the application
The purpose of Food Logger is to allow the user to keep track of the type, quantity and nutritional value of food eaten over time. The interface permits the following operations:

1. **Add food log entry**

    A form is presented to the user into which they can enter the name of the food eaten, the date it was eaten, and the quantity in grams of the food eaten. Only foods that exist in the application database are permitted. This limitation is enforced by an autocomplete function implemented in the food name field. As the user types in this field, suggestions acquired on the fly from the local application database are presented. The user can select one of these suggestions or can choose to add a food.
    

1. **Add a food item (to the application database)**

    The user is presented with a modal form containing fields for the name of the food to be added and a number of nutritional attributes of that food; i.e. calories, protein, fat, and carbohydrate levels. When the form is submitted the new food details are added to the ```food_items``` table of the application database and can then be used as logged foods in the food logger. The food name field will make suggestions as the user types. These suggestions are retrieved from the [Edamam Food Database](https://www.edamam.com/) using their [Food Search Autocomplete API](https://developer.edamam.com/food-database-api-docs). If a suggestion is accepted by the user, a subsequent call to the [Edamam Food Request Parser API](https://developer.edamam.com/food-database-api-docs) returns the required nutritional information for that food type and the ```add food``` form is auto-filled.

1. **Interaction between the add log entry form and the add food form**

    If the food name field of the log food form contains any text when the add food form is opened, the food name field of the add food form is automatically filled with that text and completion suggestions are instantly retrieved from the Edamam API. If a suggestion is then accepted and a new food added to the application database, then the log food form food name field will be automatically filled with that food's name.

1. **Edit food log entry**

    If the Log->Edit record menu item is selected the food log table enters edit mode. In this mode, when a food log entry is selected, an edit food log modal form opens and is populated with the details of the selected entry. The user can then make any changes they wish to make to the entry and save the updated record to the database.

1. **Delete food log entry**

    The Log->Delete record menu item allows the user to click on a log entry to delete it.

1. **Login and register**

    If no user is logged in the application redirects to the login page. There, a user can login or select the Register menu item to go to the register page. When a user logs in or registers they are redirected to the main application food log page.

### Deployment

The sample application is deployed on a [Linode](https://www.linode.com/) virtual private server running [Arch Linux](https://archlinux.org/) at https://data-representation-project.eu. The application is served using the [Nginx](https://docs.nginx.com/nginx/admin-guide/installing-nginx/installing-nginx-open-source/) web server. The flask application interfaces with nginx via the [Gunicorn](https://gunicorn.org) WSGI application server which is run as a (systemd) service. The application is https enabled via the [Let's Encrypt](https://letsencrypt.org/) certification authority. The nginx and systemd configurations for the application can be found in the repository's production_server_config directory.
    

