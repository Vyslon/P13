# **Projet 13 Openclassrooms - Thomas SANTONI**
## ***Application django aidant à la recherche d'emploi.***

- [1. Introduction](#1-introduction)
  * [1.1. Contexte](#11-contexte)
- [2. Procédure de déploiement de l'application](#2-procédure-de-déploiement-de-lapplication)
  * [2.1. Installation des premiers packages](#21-installation-des-premiers-packages)
  * [2.2. Mise en place de l'environnement virtuel Python](#22-mise-en-place-de-lenvironnement-virtuel-python)
  * [2.3. Installation de l'application](#23-installation-de-lapplication)
  * [2.4. Initialisation du projet](#24-initialisation-du-projet)
  * [2.5. Configuration de Gunicorn](#25-configuration-de-gunicorn)
  * [2.6. Configuration de Nginx](#26-configuration-de-nginx)

## 1. Introduction
### 1.1. Contexte
J'ai réalisé cette application web en tant que projet final pour la formation Openclassrooms : Développeur d'application - Python.
L'objectif de l'application est de permettre aux utilisateurs de trouver des entreprises recrutant autours d'eux (pour un métier donné).
Pour ce faire, l'application fais appel à l'API de pôle emploi : "La Bonne Boîte"

## 2. Procédure de déploiement de l'application
Ici, la procédure de déploiement vise un service IaaS, j'ai choisi Digital Ocean mais n'importe quel autre hébergeur fournissant une machine Ubuntu sera suffisant.
La procédure de déploiement est inspirée de celle de Digital Ocean.

### 2.1. Installation des premiers packages
Pour commencer, il faut installer les packages dont nous aurons besoin : 

```bash
sudo apt update 
sudo apt install python3-pip python3-dev libpq-dev nginx curl
```

### 2.2. Mise en place de l'environnement virtuel Python
Un environnement virtuel est un dossier contenant une installation spécifique de Python et de différentes bibliothèques, ils permettent d'éviter les conflits entre plusieurs projets python au sein d'une même machine et permettent de facilement cibler les packages important pour notre application Python. 
Ainsi, l'exportation d'un projet Python d'une machine à l'autre est aisée pour ce qui est des dépendances logicielles.

Ici, nous allons installer les packages nécessaires à la gestion de packages. 
(Nous mettons à jour pip qui gère le téléchargement de nouveaux packages et nous téléchargeons virtualenv pour créer un environnement virtuel)
```bash
sudo -H pip3 install --upgrade pip
sudo -H pip3 install virtualenv
```

Ensuite, nous allons créer un dossier dans lequel installer notre projet puis créer un environnement virtuel.
```bash
mkdir ~/jsearch
cd ~/jsearch
virtualenv jsearch
```

Enfin, on active l'environnement virtuel 
```bash
source jsearch/bin/activate
```

Voici ce qui devrait être affiché sur votre terminal, à gauche :
```bash
(jsearch)
```

L'environnement virtuel est en place, téléchargeons maintenant Django et Gunicorn : 
```bash
pip install django gunicorn
```

### 2.3. Installation de l'application
Maintenant, nous allons récupérer l'application depuis GitHub :
```bash
git clone https://github.com/Vyslon/Projet-13.git
```

Ensuite, modifions le fichier de configuration du projet, settings.py, à la ligne "ALLOWED HOSTS".
Vous devez mettre entre guillemets l'adresse de votre serveur (à trouver sur le site de votre hébergeur) :
```python
ALLOWED_HOSTS = ['165.227.166.17']
```

Désactivez le mode debug de l'application : 
```python
DEBUG = False
```

En bas du fichier settings.py, ajoutez ces lignes : 
```python
STATICFILES_DIRS = [
    "/root/jsearch/Projet-13/static"
]      

import os
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')
```

Générez une clé secrète : 
```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

Et mettez la dans le fichier settings.py : 
```python
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'lwyncfe=2g$c**l^f$r((vmxv_902#$rd*u$wpkvb$(9(t^pkg'
```

Puis sauvegardez et fermez le fichier.

### 2.4. Initialisation du projet

Téléchargez les packages nécessaires à l'application :
```bash
pip install -r ~/jsearch/Projet-13/requirements.txt
```

maintenant, initialisez le projet en commençant par faire les migrations de la structure de la base de données : 
```bash
~/jsearch/Projet-13/job_search_platform/manage.py makemigrations
~/jsearch/Projet-13/job_search_platform/manage.py migrate
```

Créez un superutilisateur pour l'administration de l'application : 
```bash
~/jsearch/Projet-13/job_search_platform/manage.py createsuperuser
```
(Pour vous connecter au site en tant qu'utilisateur, vous créer un compte manuellement en vous inscrivant sur le site)

Puis, collectez tous les fichiers statiques (html, css, javascript) :
```bash
~/jsearch/Projet-13/job_search_platform/manage.py collectstatic
```

Récupérez les données sur les métiers :
```bash
./manage.py loaddata main_platform/fixtures/datadump.json
```
(Vous pouvez aussi exécuter le script permettant de récupérer ces données à partir d'un fichier csv présent dans l'application :
```bash
./manage.py rome_codes_to_db
```
)


Autorisez le port 8000 :
```bash
sudo ufw allow 8000
```

Démarrez le serveur : 
```bash
/manage.py runserver 0.0.0.0:8000
```

Enfin, visitez votre adresse pour voir si l'application web est installée : 
```bash
http://adresseDeVotreServeur:8000/
```

### 2.5. Configuration de Gunicorn

Allez à la racine du projet puis lancez gunicorn :
```bash
cd ~/jsearch/Projet-13/job_search_platform
gunicorn --bind 0.0.0.0:8000 job_search_platform.wsgi
```

Rouvrez votre navigateur à l'adresse précèdente et vérifier que tout fonctionne (les fichiers CSS/JS ne sont toujours pas actifs).

Puis faites CTRL+C dans le terminal et sortez de l'environnement virtuel
```bash
deactivate
```

Maintenant, créez un fichier socket pour gunicorn : 
```bash
sudo vi /etc/systemd/system/gunicorn.socket
```

Et copiez ceci à l'intérieur : 
```bash
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
```
Sauvegardez et quittez.

Maintenant, créez un fichier de service systemd
```bash
sudo vi /etc/systemd/system/gunicorn.service
```

Copiez ceci dans le fichier : 
```bash
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=django
Group=www-data
WorkingDirectory=/root/jsearch/
ExecStart=/root/jsearch/jsearch/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/run/gunicorn.sock \
          job_search_platform.wsgi:application

[Install]
WantedBy=multi-user.target
```

Puis, démarrez et activez le socket Gunicorn : 
```bash
sudo systemctl start gunicorn.socket
sudo systemctl enable gunicorn.socket
```

Enfin, vérifiez le statut du socket :
```bash
sudo systemctl status gunicorn.socket
```

Vous devriez voir (entre autres) ceci :
```bash
Loaded : loaded
Active : active
```

Vérifiez l'existence du fichier gunicorn.sock :
```bash
file /run/gunicorn.sock
```

Résultat attendu : 
```bash
/run/gunicorn.sock: socket
```

Testons maintenant la connexion : 
```bash
curl --unix-socket /run/gunicorn.sock adresseDeVotreServeur:8000
```

Si tout a fonctionné, vous allez recevoir une page HTML, la page d'inscription.

### 2.6. Configuration de Nginx
Pour commencer, créez un fichier dans sites-available de nginx : 
```bash
sudo vi /etc/nginx/sites-available/job_search_platform
```

Remplissez le comme ceci : 
```bash
server {
    listen 80;
    server_name adresseDeVotreServeur;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        alias /root/jsearch/Projet-13/static;
    }
    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }
}
```

Maintenant nous pouvons activer le fichier en le liant à sites-enables :
```bash
sudo ln -s /etc/nginx/sites-available/job_search_platform /etc/nginx/sites-enabled
```

Vérifiez les erreurs de syntaxe en faisant appel à cette commande :
```bash
sudo nginx -t
```

S'il n'y a plus d'erreurs, redémarrez nginx : 
```bash
sudo systemctl restart nginx
```

Nous accéderons maintenant à l'application web par le port 80, nous allons donc supprimer l'accès au port 8000 :
```bash
sudo ufw delete allow 8000
sudo ufw allow 'Nginx Full'
```

Vous pouvez maintenant accéder à l'application à l'adresse http://adresseDeVotreServeur/
(exemple : http://165.227.166.17/)














