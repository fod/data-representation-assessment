# settings.py
# Food app settings file
# Author: Fiachra O' Donoghue
# https://gist.github.com/fod/7437a5931192c295d37dd532d8b01176

EDAMAM_AUTOCOMPLETE_BASE_URL =  "https://api.edamam.com/auto-complete"
EDAMAM_PARSER_BASE_URL = "https://api.edamam.com/api/food-database/v2/parser"
EDAMAM_APP_ID = "PUT EDAMAM APP ID HERE"
EDAMAM_API_KEY = "PUT EDAMAM API KEY HERE"

MYSQL_HOST = "PUT HOSTNAME HERE" #localhost for local; 
MYSQL_USER = "PUT MYSQL USERNAME HERE"
MYSQL_PASSWORD = "PUT MYSQL PASSWORD HERE"
MYSQL_DB = "food"

SECRET_KEY = "PUT A STRING OF RANDOM BYTES (FOR FLASK SECRET KEY) HERE"
