# Business Impact Assessment Application!

This application is designed to facilitate Business Impact Assessments (BIAs) within organizations. It's built using Python and Flask. 
**Update 19-06-2025** : The application can now also be deployed with a "real" SQL backend, so it can be run for an entire organisation.

## Setup Instructions

### Prerequisites

- Python 3.12 or higher
- pip (Python package installer)

### 1. Clone the Repository

```bash
git clone https://github.com/fstelte/business-impact-assessment.git
cd business-impact-assessment
```

### 2. Create and Activate a Virtual Environment

On MacOS and Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

On Windows (I do recommend running WSL on Windows..)

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set environment variables

Create a .env file in the root directory of the project and add the following:

```bash
DATABASE_TYPE=sqlite
#DATABASE_TYPE=mariadb

# Enter your admin credentials here
ADMIN_EMAIL="example@example.com"
ADMIN_PASSWORD="aVerySecurePasswordSh0uldBeUsedH3r3!"

# .env - MariaDB Database Credentials
# Be aware: do no use quotes around the values

DB_USER=<db_username>
DB_PASSWORD=<db_password>
DB_HOST=<db_host>
DB_PORT=<db_port>
DB_NAME=<db_name>

# Keep secret key here
SECRET_KEY=een_andere_geheime_sleutel_voor_flask
```

Replace your_secret_key_here, admin@example.com, and secure_password_here with your actual secret key, admin email, and admin password.
Also choose the database type, you can choose between sqlite or mariadb/mysql

If you choose to use mariadb/mysql you should also fill you the variables DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME the application assumes you have setup the server and empty database already.

### 5. Initialize the database

Make sure you have the instance folder created in the root of the application

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 6. Creat the admin user

```bash
flask create-admin
```

This command will use the ADMIN_EMAIL and ADMIN_PASSWORD from your .env file to create an admin user.

### 7. Run the application

```bash
python run.py
```

The application will start and be accessible at http://localhost:5001.

## Usage

1. Open a web browser and navigate to http://localhost:5001.
2. Log in with the admin credentials you set up.
3. Use the navigation bar to manage BIAs, components, consequences, and availability requirements.

## Additional Information

For more detailed information about the application's features and how to use them, please refer to the application's documentation or contact the development team.
