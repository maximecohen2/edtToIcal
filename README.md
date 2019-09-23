# EDT TO ICAL


## Installation

Il faut créer un envirenoment virtuel puis exécuter la commande suivante :

```
pip install -r requirements.txt
```

## Usage

```
usage: edtToIcal.py <StudentLogin> [OPTIONS]

Récupère l'emplois du temps de l'étudiant et le retourne au format iCal

positional arguments:
  StudentLogin          Login de l'étudiant

optional arguments:
  -h, --help            show this help message and exit
  -n FILENAME, --filename FILENAME
                        Nom du fichier
  -t TARGET_DIRECTORY, --target-directory TARGET_DIRECTORY
                        Destination du fichier (défaut: "./")
  -d DATE, --date DATE  Date d'une journée de la semaine cible (défaut:
                        aujourd'hui) (ex: 25/12/2000)
  -w NUMBER_WEEK, --number-week NUMBER_WEEK
                        Nombre de semaine à récupérer à partir de la date
```
