#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
import os

from nagios_manager import NagiosManager
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Initialiser le gestionnaire Nagios
nagios_mgr = NagiosManager(app.config['NAGIOS_BASE_PATH'])

# Décorateur pour l'authentification
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if app.config['REQUIRE_AUTH'] and 'username' not in session:
            return jsonify({'error': 'Non authentifié'}), 401
        return f(*args, **kwargs)
    return decorated_function

# Routes d'authentification
from passlib.apache import HtpasswdFile

# Charger le fichier htpasswd au démarrage
htpasswd = HtpasswdFile(app.config['HTPASSWD_FILE'])

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    try:
        # Vérifier si l'utilisateur existe et si le mot de passe est correct
        if htpasswd.check_password(username, password):
            session['username'] = username
            return jsonify({'success': True, 'username': username})
        else:
            return jsonify({'success': False, 'error': 'Identifiants invalides'}), 401
    except Exception as e:
        print(f"Erreur lors de la vérification du login: {e}")
        return jsonify({'success': False, 'error': 'Erreur serveur'}), 500


@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return jsonify({'success': True})

@app.route('/api/check-auth', methods=['GET'])
def check_auth():
    if not app.config['REQUIRE_AUTH']:
        return jsonify({'authenticated': True, 'username': 'demo'})

    if 'username' in session:
        return jsonify({'authenticated': True, 'username': session['username']})

    return jsonify({'authenticated': False}), 401

# Routes API pour les hôtes
@app.route('/api/hosts', methods=['GET'])
@login_required
def get_hosts():
    '''Récupère tous les hôtes'''
    try:
        hosts = nagios_mgr.get_all_hosts()
        return jsonify({'success': True, 'hosts': hosts})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/hosts/<host_name>', methods=['GET'])
@login_required
def get_host(host_name):
    '''Récupère un hôte spécifique'''
    try:
        host = nagios_mgr.get_host_by_name(host_name)
        if host:
            return jsonify({'success': True, 'host': host})
        else:
            return jsonify({'success': False, 'error': 'Hôte introuvable'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/hosts', methods=['POST'])
@login_required
def create_host():
    '''Crée un nouvel hôte'''
    try:
        data = request.get_json()
        host_data = data.get('host')
        directory = data.get('directory')

        if not host_data or not directory:
            return jsonify({'success': False, 'error': 'Données invalides'}), 400

        success = nagios_mgr.create_host(host_data, directory)

        if success:
            # Valider la configuration
            valid, output = nagios_mgr.validate_configuration()

            if valid:
                return jsonify({
                'success': True,
                'message': 'Hôte créé avec succès',
                'validation': output
            })
            else:
            # NE PAS supprimer pour voir l'erreur
            # nagios_mgr.delete_host(host_data['host_name'])  # Commenté temporairement
            
                return jsonify({
                'success': False,
                'error': 'Configuration invalide',
                'validation': output  # ← Message d'erreur Nagios
            }), 400
        else:
            return jsonify({'success': False, 'error': 'Échec de la création'}), 500

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/hosts/<host_name>', methods=['PUT'])
@login_required
def update_host(host_name):
    '''Met à jour un hôte'''
    try:
        data = request.get_json()
        host_data = data.get('host')

        if not host_data:
            return jsonify({'success': False, 'error': 'Données invalides'}), 400

        success = nagios_mgr.update_host(host_name, host_data)

        if success:
            # Valider la configuration
            valid, output = nagios_mgr.validate_configuration()

            if valid:
                return jsonify({
                    'success': True,
                    'message': 'Hôte mis à jour avec succès',
                    'validation': output
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Configuration invalide',
                    'validation': output
                }), 400
        else:
            return jsonify({'success': False, 'error': 'Échec de la mise à jour'}), 500

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/hosts/<host_name>', methods=['DELETE'])
@login_required
def delete_host(host_name):
    '''Supprime un hôte'''
    try:
        success = nagios_mgr.delete_host(host_name)

        if success:
            return jsonify({
                'success': True,
                'message': f'Hôte {host_name} supprimé avec succès'
            })
        else:
            return jsonify({'success': False, 'error': 'Échec de la suppression'}), 500

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/directories', methods=['GET'])
@login_required
def get_directories():
    '''Liste tous les répertoires disponibles'''
    try:
        directories = nagios_mgr.get_directories()
        return jsonify({'success': True, 'directories': directories})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/validate', methods=['POST'])
@login_required
def validate_config():
    '''Valide la configuration Nagios'''
    try:
        valid, output = nagios_mgr.validate_configuration()
        return jsonify({
            'success': True,
            'valid': valid,
            'output': output
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/restart', methods=['POST'])
@login_required
def restart_nagios():
    '''Redémarre Nagios'''
    try:
        # D'abord valider
        valid, validation_output = nagios_mgr.validate_configuration()

        if not valid:
            return jsonify({
                'success': False,
                'error': 'Configuration invalide',
                'output': validation_output
            }), 400

        # Redémarrer
        success, output = nagios_mgr.restart_nagios()

        return jsonify({
            'success': success,
            'message': 'Nagios redémarré avec succès' if success else 'Échec du redémarrage',
            'output': output
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Route pour servir l'application web
@app.route('/')
def index():
	return render_template('index.html')
if __name__ == '__main__':
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )
