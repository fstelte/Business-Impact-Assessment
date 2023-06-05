# Business-Impact-Assessment

A web application to (localy) conduct Business Impact Assessments

The intended use of this application is to run this locally on your laptop, but there is nothing withholding you to create a public service with this (I would personally add some form of authentication, because the info can be very sensitive).
Built on python, flask and some extenions for flask.

This application can be used by anyone in any circumstance (commercial, non-commercial, business, personal), only thing I ask of you is to provide credits for the original work that has been done to get this application to work. It would be great if an active community would help me maintain and built out the capabilities of this application.

## Pre requisists:

 1. Python3 running on your device (https://www.python.org/downloads/)
 2. PIP running on your devices (https://www.makeuseof.com/tag/install-pip-for-python/)

## Getting ready to run

### (git clone) Clone this repository to your device
  
    git clone https://github.com/fstelte/Business-Impact-Assessment.git
  
 Go into directory and run:
  
    pip install -r requirements.txt

Create a file named **mysecrets.py** in the root folder

from within python run (python3):

    import os
    os.urandom(61).hex()
Put the hex value in the mysecrets.py like so *SECRET_KEY = "HEXVALUE"*

 After this finishes, create the database:
  
    alembic revision --autogenerate -m "create db"
    alembic upgrade head

 **Adding the default values** 
 
 Now included is the **default_values.sql**
 ``` python3 first_run_default_values.py ```

### Create entries in security_properties
  
```Standard I use Confidentiality, Integrity, Availability```
  
### Create entries in consequence_choices
  
```I use Low, Medium, High, Huge```
  
### Create entries in references
  
```I use Financial, Operational, Regulatory, Reputation and Trust, Human and Safety, Privacy```


  
 You are now good to go.
  
### Run the application

    python3 run.py

``` WHEN ON MACOS AND YOU HAVE AIRPLAY ENABLED, YOU NEED TO EDIT *run.py* TO CHANGE THE PORT TO 5001 OR TO YOUR CHOOSING``` 

 Open a browser and head to http://127.0.0.1:5000

# ToDo list:

- When editing have the values in the field reflect the values in the database
- Built-in reporting
 - 
