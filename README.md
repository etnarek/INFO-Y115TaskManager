# Installation

Dépendances : `python3`, `postgresql`

    virtualenv ve
    source ve/bin/activate
    pip install -r requirements.txt
    createdb taskManager
    psql -d taskManager -f createdb.sql

# Configuration et démarrage

Editez `local_config.py` pour écraser les valeurs par défaut spécifiées dans `config.py`.

Démarrez l'app avec :

    python app.py
