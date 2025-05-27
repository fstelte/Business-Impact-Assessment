# English
## Table of Contents
1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Project Structure](#project-structure)
4. [Installation](#installation)
5. [Usage](#usage)
6. [Contributing](#contributing)
7. [Testing](#testing)
8. [License](#license)
9. [Contact](#contact)
10. [Dependencies](#dependencies)
11. [Troubleshooting](#troubleshooting)

## Project Overview
**Business-Impact-Assessment** is a web application built with **Python**, **Flask**, and various Flask extensions. It's designed for conducting local **Business Impact Assessments (BIAs)**. A BIA is a crucial process that helps organizations identify and prioritize their critical business functions and the impact of disruptions to them.


## Features
* Create and manage BIAs
* Add and manage components within BIAs
* Assign consequences to components
* Define availability requirements per component
* Generate BIA reports


## Project Structure
* `/app`: Contains the main application code
    * `/blueprints`: Flask blueprints for different functionalities
    * `/templates`: HTML templates for the user interface
* `/alembic`: Contains database migration scripts
* `config.py`: Configuration settings for the application
* `run.py`: The application's entry point



## Installation
1.  Ensure **Python3** and **PIP** are installed on your device.
2.  Clone the repository:
    ```bash
    git clone [https://github.com/fstelte/Business-Impact-Assessment.git](https://github.com/fstelte/Business-Impact-Assessment.git)
    ```
3.  Navigate to the project directory:
    ```bash
    cd Business-Impact-Assessment
    ```
4.  Create a Python virtual environment:
    ```bash
    python -m venv venv
    ```
5.  Activate the virtual environment:
    * On Windows: `venv\Scripts\activate`
    * On macOS and Linux: `source venv/bin/activate`
6.  Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```
7.  Create a `.env` file in the root directory and set the secret key:
    ```
    SECRET_KEY=your_secret_key_here
    ```
8.  Create the database:
    ```bash
    alembic revision --autogenerate -m "create db"
    alembic upgrade head
    ```
9.  Add default values:
    ```bash
    python3 first_run_default_values.py
    ```

## Usage
1.  Start the application:
    ```bash
    python3 run.py
    ```
2.  Open a web browser and go to `http://localhost:5001`
3.  Use the navigation bar to manage BIAs, components, consequences, and availability requirements.


## Contributing
Contributions to this project are welcome. You can contribute as follows:
1.  Fork the repository
2.  Create a new branch for your feature
3.  Commit your changes
4.  Push to the branch
5.  Create a new Pull Request


## Testing
(Here you can add information on how to run tests, if tests are available)


## License
This project is available for commercial, non-commercial, and personal use. When using, please provide credit to the original work.


## Contact
For questions or support, please contact via [your contact information].


## Dependencies
* Flask
* Flask-WTF
* Flask-Bootstrap
* SQLAlchemy
* WTForms
* Python-dotenv

For a complete list, see `requirements.txt`.


## Troubleshooting
(Here you can add common problems and their solutions)

# Nederlands
# Business Impact Assessment Tool

## Inhoudsopgave
1. [Projectoverzicht](#projectoverzicht)
2. [Functionaliteiten](#functionaliteiten)
3. [Projectstructuur](#projectstructuur)
4. [Installatie](#installatie)
5. [Gebruik](#gebruik)
6. [Bijdragen](#bijdragen)
7. [Testen](#testen)
8. [Licentie](#licentie)
9. [Contact](#contact)
10. [Afhankelijkheden](#afhankelijkheden)
11. [Troubleshooting](#troubleshooting)

## Projectoverzicht
Business-Impact-Assessment is een web applicatie gebouwd met Python, Flask, en diverse Flask extensies. Het is ontworpen voor het uitvoeren van lokale Business Impact Assessments (BIA's). Een BIA is een cruciaal proces dat organisaties helpt bij het identificeren en prioriteren van hun kritieke bedrijfsfuncties en de impact van verstoringen hierop.

## Functionaliteiten
- Creëren en beheren van BIA's
- Toevoegen en beheren van componenten binnen BIA's
- Toewijzen van consequenties aan componenten
- Definiëren van beschikbaarheidsvereisten per component
- Genereren van BIA rapporten

## Projectstructuur
- `/app`: Bevat de hoofdapplicatiecode
  - `/blueprints`: Flask blueprints voor verschillende functionaliteiten
  - `/templates`: HTML-templates voor de gebruikersinterface
- `/alembic`: Bevat database migratie scripts
- `config.py`: Configuratie-instellingen voor de applicatie
- `run.py`: Het startpunt van de applicatie

## Installatie
1. Zorg ervoor dat Python3 en PIP zijn geïnstalleerd op uw apparaat.
2. Clone de repository:
``` bash
   git clone https://github.com/fstelte/Business-Impact-Assessment.git
``` 
Navigeer naar de projectdirectory:
``` bash
   cd Business-Impact-Assessment
```
4. Maak een Python virtuele omgeving aan:
```bash
   python -m venv venv
```
5. Activeer de virtuele omgeving:
- Op Windows: `venv\Scripts\activate`
- Op macOS en Linux: `source venv/bin/activate`
6. Installeer de vereiste pakketten:
```bash
   pip install -r requirements.txt
```
7. Maak een `.env` bestand aan in de hoofdmap en stel de geheime sleutel in:
   SECRET_KEY=uw_geheime_sleutel_hier
8. Maak de database aan:
   alembic revision --autogenerate -m "create db"
   alembic upgrade head
9. Voeg standaardwaarden toe:
   python3 first_run_default_values.py

## Gebruik
1. Start de applicatie:
   python3 run.py
2. Open een webbrowser en ga naar `http://localhost:5001`
3. Gebruik de navigatiebalk om BIA's, componenten, consequenties en beschikbaarheidsvereisten te beheren.

## Bijdragen
Bijdragen aan dit project zijn welkom. U kunt als volgt bijdragen:
1. Fork de repository
2. Maak een nieuwe branch voor uw functie
3. Commit uw wijzigingen
4. Push naar de branch
5. Maak een nieuwe Pull Request

## Testen
(Hier kunt u informatie toevoegen over hoe tests uit te voeren, als er tests beschikbaar zijn)

## Licentie
Dit project is beschikbaar voor commercieel, niet-commercieel en persoonlijk gebruik. Bij gebruik wordt verzocht om credits te geven aan het originele werk.

## Contact
Voor vragen of ondersteuning, neem contact op via [uw contactinformatie].

## Afhankelijkheden
- Flask
- Flask-WTF
- Flask-Bootstrap
- SQLAlchemy
- WTForms
- Python-dotenv

Voor een volledige lijst, zie `requirements.txt`.

## Troubleshooting
(Hier kunt u veelvoorkomende problemen en hun oplossingen toevoegen)

