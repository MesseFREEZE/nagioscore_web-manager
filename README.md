# Nagios Web Configuration Manager

Interface web moderne pour gérer les configurations d'hôtes Nagios Core depuis un navigateur.

Version 1

## Fonctionnalités

- ✅ Liste tous les hôtes Nagios configurés
- ✅ Recherche et filtrage des hôtes
- ✅ Création de nouveaux hôtes via formulaire web
- ✅ Modification des hôtes existants
- ✅ Suppression d'hôtes avec confirmation
- ✅ Scan automatique de tous les sous-répertoires de /usr/local/nagios/etc
- ✅ Authentification nagios

## Architecture

```
nagios-web-config/
├── app.py                  # Application Flask (API REST)
├── nagios_manager.py       # Module de gestion des fichiers Nagios
├── config.py              # Configuration de l'application
├── requirements.txt       # Dépendances Python
└── index.html            # Interface web 
```

## Prérequis

- Python 3.6+
- Nagios Core installé (typiquement dans /usr/local/nagios)
- Droits d'accès en lecture/écriture sur /usr/local/nagios/etc
- Droits pour exécuter systemctl restart nagios (ou équivalent)

## Installation

### 1. Cloner ou télécharger les fichiers

```bash
mkdir -p /opt/nagios-web-config
cd /opt/nagios-web-config
```

Placez tous les fichiers Python dans ce répertoire.

### 2. Installer les dépendances Python

```bash
# Créer un environnement virtuel (recommandé)
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

### 3. Configuration

Modifiez `config.py` selon votre installation :

```python
# Chemin de base Nagios
NAGIOS_BASE_PATH = '/usr/local/nagios/etc'

# Binaire Nagios
NAGIOS_BIN = '/usr/local/nagios/bin/nagios'
```

Ou utilisez des variables d'environnement :

Générer une SECRET_KEY avec : python3 -c 'import secrets; print(secrets.token_hex(32))'


```bash
export NAGIOS_BASE_PATH=/usr/local/nagios/etc
export NAGIOS_BIN=/usr/local/nagios/bin/nagios
export FLASK_DEBUG=False
export SECRET_KEY=votre-cle-secrete-aleatoire
```

### 4. Droits d'accès

L'utilisateur qui exécute l'application doit avoir :

```bash
# Lecture/écriture sur les configs
chmod -R 664 /usr/local/nagios/etc/*.cfg
chgrp -R nagios /usr/local/nagios/etc

# Ajouter l'utilisateur au groupe nagios
usermod -aG nagios votre_utilisateur

# Pour le redémarrage via systemctl
# Ajouter dans /etc/sudoers.d/nagios-web-config :
votre_utilisateur ALL=(ALL) NOPASSWD: /bin/systemctl restart nagios
```

## Utilisation

### Démarrer l'application Flask

```bash
# Mode développement
python app.py

# Ou avec Flask CLI
export FLASK_APP=app.py
flask run --host 0.0.0.0 --port 5000
```

### Mode production avec Gunicorn

```bash
# Installer gunicorn
pip install gunicorn

# Lancer l'application
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Utiliser l'interface web

1. Ouvrez votre navigateur : `http://votre-serveur:5000`
2. Connectez-vous avec vos identifiants -> Connexion par HTPASSWD.USERS (login nagios)
3. Utilisez l'interface pour :
   - Voir tous vos hôtes configurés
   - Créer de nouveaux hôtes
   - Modifier les hôtes existants
   - Supprimer des hôtes

### Utiliser l'API REST

L'application expose aussi une API REST :

```bash
# Authentification
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"nagios123"}' \
  -c cookies.txt

# Lister tous les hôtes
curl -X GET http://localhost:5000/api/hosts \
  -b cookies.txt

# Obtenir un hôte spécifique
curl -X GET http://localhost:5000/api/hosts/web-server-01 \
  -b cookies.txt

# Créer un nouvel hôte
curl -X POST http://localhost:5000/api/hosts \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "directory": "/usr/local/nagios/etc/servers",
    "host": {
      "host_name": "nouveau-serveur",
      "alias": "Nouveau Serveur",
      "address": "192.168.1.50",
      "use": "linux-server",
      "check_command": "check-host-alive",
      "max_check_attempts": "5",
      "check_interval": "5",
      "retry_interval": "1",
      "notification_interval": "30",
      "notification_period": "24x7",
      "contacts": "nagiosadmin",
      "contact_groups": "admins"
    }
  }'

# Modifier un hôte
curl -X PUT http://localhost:5000/api/hosts/web-server-01 \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "host": {
      "host_name": "web-server-01",
      "alias": "Serveur Web Modifié",
      "address": "192.168.1.10",
      "use": "linux-server"
    }
  }'

# Supprimer un hôte
curl -X DELETE http://localhost:5000/api/hosts/old-server \
  -b cookies.txt

# Valider la configuration
curl -X POST http://localhost:5000/api/validate \
  -b cookies.txt

# Redémarrer Nagios
curl -X POST http://localhost:5000/api/restart \
  -b cookies.txt
```

## Fonctionnement

### 1. Scanner les configurations

Le module `NagiosManager` scanne récursivement tous les sous-répertoires de `/usr/local/nagios/etc` et identifie tous les fichiers `.cfg` contenant des définitions d'hôte, il exclue "objects"

### 2. Parser les fichiers

Les fichiers sont parsés avec des expressions régulières pour extraire :
- Les blocs `define host { ... }`
- Toutes les directives Nagios (host_name, alias, address, etc.)

### 3. Gérer les hôtes

L'application permet de :
- **Créer** : Génère un nouveau fichier .cfg et l'ajoute à nagios.cfg
- **Modifier** : Met à jour le bloc de définition dans le fichier existant
- **Supprimer** : Retire la définition ou supprime le fichier si vide

### 4. Valider et appliquer

Avant chaque modification :
1. La configuration est validée avec `nagios -v /usr/local/nagios/etc/nagios.cfg`
2. Si valide, la modification est conservée
3. Si invalide, la modification est annulée
4. L'utilisateur peut ensuite redémarrer Nagios pour appliquer les changements

## Sécurité

⚠️ **IMPORTANT** - Recommandations de sécurité :

1. **Changez les mots de passe par défaut** dans `config.py`
2. **Utilisez HTTPS** en production (reverse proxy nginx/apache)
3. **Limitez l'accès** avec un firewall (iptables/firewalld)
4. **Activez l'authentification** (`REQUIRE_AUTH = True`)
5. **Utilisez des secrets forts** pour `SECRET_KEY`
6. **Restreignez les droits** de l'utilisateur qui exécute l'app
7. **Loggez les actions** pour l'audit

## Personnalisation

### Ajouter d'autres types d'objets

Le module `nagios_manager.py` peut être étendu pour gérer :
- Services
- Contacts
- Groupes d'hôtes
- Commandes
- Templates



## Dépannage

### Erreur de permission

```bash
# Vérifier les droits
ls -la /usr/local/nagios/etc/

# Ajuster si nécessaire
chown -R nagios:nagios /usr/local/nagios/etc/
chmod -R 775 /usr/local/nagios/etc/
```

### Nagios ne redémarre pas

```bash
# Vérifier le service
systemctl status nagios

# Vérifier la configuration manuellement
/usr/local/nagios/bin/nagios -v /usr/local/nagios/etc/nagios.cfg

# Voir les logs
tail -f /usr/local/nagios/var/nagios.log
```

### L'application ne trouve pas les hôtes

Vérifiez que :
1. Le chemin `NAGIOS_BASE_PATH` est correct
2. Les fichiers .cfg existent et contiennent `define host {`
3. Les droits de lecture sont corrects

## Contribution
Toute aide est la bienvenue

Pour améliorer ce projet :

1. Ajoutez la gestion des services Nagios
2. Créez des templates d'hôtes réutilisables
3. Ajoutez des graphiques et statistiques

## Licence

Ce projet est fourni tel quel pour faciliter la gestion de Nagios Core.
Adaptez-le à vos besoins spécifiques.

## Auteur
Mathis HEIN
Créé pour simplifier la gestion des configurations Nagios Core via interface web.
