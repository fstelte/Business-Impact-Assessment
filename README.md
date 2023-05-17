# Business-Impact-Assessment
A web application to (localy) conduct Business Impact Assessments

The intended use of this application is to run this locally on your laptop, but there is nothing withholding you to create a public service with this (I would personally add some form of authentication, because the info can be very sensitive).
Built on python, flask and some extenions for flask.

This application can be used by anyone in any circumstance (commercial, non-commercial, business, personal), only thing I ask of you is to provide credits for the original work that has been done to get this application to work. It would be great if an active community would help me maintain and built out the capabilities of this application.

## Pre requisists:
 1. Python3 running on your device (https://www.python.org/downloads/)
 2. PIP running on your devices (https://www.makeuseof.com/tag/install-pip-for-python/)

 ## Getting ready to run:

 **(git clone) Clone this repository to your device.**
 
 Go into directory and run:
 
 pip install -r requirements.txt

 After this finishes enter:

 **Create the database**
 
 alembic revision --autogenerate -m "create db"
 
 
 alembic upgrade head
 
**Run the application**

 python3 run.py

 Open a browser and head to http://127.0.0.1:5000


 # ToDo list:
 - When editing have the values in the field reflect the values in the database
 - Built-in reporting
 - 
