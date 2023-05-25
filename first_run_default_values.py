import sqlite3

connection = sqlite3.connect('bia.db')


with open('default_values.sql') as f:
    connection.executescript(f.read())

#with open('create_schema.sql') as f:
#    connection.executescript(f.read())
