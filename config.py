#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os

class Config:
    '''Configuration de l'application Flask'''
    
    # Clé secrète Flask (à changer en production)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production-use-environment'
    
    # Configuration Nagios
    NAGIOS_BASE_PATH = os.environ.get('NAGIOS_BASE_PATH') or '/usr/local/nagios/etc'
    NAGIOS_BIN = os.environ.get('NAGIOS_BIN') or '/usr/local/nagios/bin/nagios'
    NAGIOS_CFG = os.path.join(NAGIOS_BASE_PATH, 'nagios.cfg')
    
    # Fichier htpasswd Nagios pour l'authentification
    HTPASSWD_FILE = os.environ.get('HTPASSWD_FILE') or '/usr/local/nagios/etc/htpasswd.users'
    
    # Configuration Flask
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    HOST = os.environ.get('FLASK_HOST') or '0.0.0.0'
    PORT = int(os.environ.get('FLASK_PORT', 5000))
    
    # Sécurité
    REQUIRE_AUTH = os.environ.get('REQUIRE_AUTH', 'True').lower() == 'true'
