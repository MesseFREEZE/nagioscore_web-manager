#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import subprocess
from typing import List, Dict, Optional

class NagiosManager:
    '''
    Gestionnaire pour les fichiers de configuration Nagios Core
    '''

    def __init__(self, nagios_base_path: str = '/usr/local/nagios/etc'):
        self.nagios_base_path = nagios_base_path
        self.nagios_cfg = os.path.join(nagios_base_path, 'nagios.cfg')
        self.nagios_bin = '/usr/local/nagios/bin/nagios'

    def find_host_files(self) -> List[str]:
        '''
        Recherche tous les fichiers .cfg contenant des définitions d'hôtes
        dans tous les sous-répertoires (sauf objects)
        '''
        host_files = []
        
        # Répertoires à exclure
        excluded_dirs = ['objects']
        
        for root, dirs, files in os.walk(self.nagios_base_path):
            # Exclure les répertoires indésirables
            dirs[:] = [d for d in dirs if d not in excluded_dirs]
            
            for file in files:
                if file.endswith('.cfg'):
                    file_path = os.path.join(root, file)
                    if self._contains_host_definition(file_path):
                        host_files.append(file_path)
        
        return host_files


    def _contains_host_definition(self, file_path: str) -> bool:
        '''Vérifie si un fichier contient une définition d'hôte'''
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                return 'define host' in content.lower()
        except:
            return False

    def parse_host_file(self, file_path: str) -> List[Dict]:
        '''
        Parse un fichier de configuration et extrait toutes les définitions d'hôtes
        '''
        hosts = []

        try:
            with open(file_path, 'r') as f:
                content = f.read()

            # Regex pour extraire les blocs define host
            host_pattern = r'define\s+host\s*\{([^}]+)\}'
            matches = re.finditer(host_pattern, content, re.DOTALL | re.IGNORECASE)

            for match in matches:
                host_block = match.group(1)
                host_data = self._parse_host_block(host_block)
                host_data['file_path'] = file_path
                host_data['directory'] = os.path.dirname(file_path)
                hosts.append(host_data)

        except Exception as e:
            print(f"Erreur lors de la lecture de {file_path}: {e}")

        return hosts

    def _parse_host_block(self, block: str) -> Dict:
        '''Parse un bloc de définition d'hôte'''
        host_data = {}

        # Regex pour extraire les directives
        directive_pattern = r'^\s*([a-z_]+)\s+(.+)$'

        for line in block.split('\n'):
            line = line.strip()
            # Ignorer les commentaires
            if line.startswith('#') or not line:
                continue

            match = re.match(directive_pattern, line, re.IGNORECASE)
            if match:
                key = match.group(1).strip()
                value = match.group(2).strip()
                # Enlever les commentaires en fin de ligne
                if '#' in value:
                    value = value[:value.index('#')].strip()
                host_data[key] = value

        return host_data

    def get_all_hosts(self) -> List[Dict]:
        '''Récupère tous les hôtes configurés'''
        all_hosts = []
        host_files = self.find_host_files()

        for file_path in host_files:
            hosts = self.parse_host_file(file_path)
            all_hosts.extend(hosts)

        return all_hosts

    def get_host_by_name(self, host_name: str) -> Optional[Dict]:
        '''Récupère un hôte par son nom'''
        all_hosts = self.get_all_hosts()

        for host in all_hosts:
            if host.get('host_name') == host_name:
                return host

        return None

    def create_host(self, host_data: Dict, directory: str) -> bool:
        '''
        Crée un nouveau fichier de configuration pour un hôte
        '''
        try:
            host_name = host_data.get('host_name')
            if not host_name:
                raise ValueError("host_name est requis")

            # CORRECTION : gérer les chemins absolus et relatifs
            if directory.startswith('/'):
                # Chemin absolu déjà fourni
                full_dir_path = directory
            else:
                # Chemin relatif, on le combine avec la base
                full_dir_path = os.path.join(self.nagios_base_path, directory)

            # Vérifier que le répertoire existe, sinon le créer
            if not os.path.exists(full_dir_path):
                os.makedirs(full_dir_path, mode=0o775)

            # Chemin du fichier
            file_path = os.path.join(full_dir_path, f"{host_name}.cfg")

            # Vérifier que le fichier n'existe pas déjà
            if os.path.exists(file_path):
                raise FileExistsError(f"Le fichier {file_path} existe déjà")

            # Générer le contenu du fichier
            content = self._generate_host_config(host_data)

            # Écrire le fichier
            with open(file_path, 'w') as f:
                f.write(content)

            # Ajouter le fichier à nagios.cfg si nécessaire
            self._add_cfg_file_to_nagios_cfg(file_path)

            return True

        except Exception as e:
            print(f"Erreur lors de la création de l'hôte: {e}")
            import traceback
            traceback.print_exc()
            return False

    def update_host(self, original_host_name: str, host_data: Dict) -> bool:
        '''
        Met à jour un hôte existant
        '''
        try:
            # Trouver l'hôte existant
            existing_host = self.get_host_by_name(original_host_name)
            if not existing_host:
                raise ValueError(f"Hôte {original_host_name} introuvable")

            file_path = existing_host['file_path']

            # Lire le fichier complet
            with open(file_path, 'r') as f:
                content = f.read()

            # Remplacer le bloc de l'hôte
            new_block = self._generate_host_config(host_data)

            # Pattern pour trouver le bloc de l'hôte
            pattern = r'define\s+host\s*\{[^}]+host_name\s+' + re.escape(original_host_name) + r'[^}]*\}'

            if re.search(pattern, content, re.DOTALL | re.IGNORECASE):
                new_content = re.sub(pattern, new_block, content, flags=re.DOTALL | re.IGNORECASE)

                # Écrire le fichier mis à jour
                with open(file_path, 'w') as f:
                    f.write(new_content)

                return True
            else:
                raise ValueError(f"Définition de l'hôte {original_host_name} introuvable dans {file_path}")

        except Exception as e:
            print(f"Erreur lors de la mise à jour de l'hôte: {e}")
            import traceback
            traceback.print_exc()
            return False

    def delete_host(self, host_name: str) -> bool:
        '''
        Supprime un hôte
        '''
        try:
            # Trouver l'hôte
            host = self.get_host_by_name(host_name)
            if not host:
                raise ValueError(f"Hôte {host_name} introuvable")

            file_path = host['file_path']

            # Lire le fichier
            with open(file_path, 'r') as f:
                content = f.read()

            # Supprimer le bloc de l'hôte
            pattern = r'define\s+host\s*\{[^}]+host_name\s+' + re.escape(host_name) + r'[^}]*\}'
            new_content = re.sub(pattern, '', content, flags=re.DOTALL | re.IGNORECASE)

            # Si le fichier ne contient plus de définitions, le supprimer
            if not self._contains_host_definition_in_text(new_content):
                os.remove(file_path)
                print(f"Fichier {file_path} supprimé")
            else:
                # Sinon, réécrire le fichier sans l'hôte
                with open(file_path, 'w') as f:
                    f.write(new_content)
                print(f"Hôte {host_name} supprimé de {file_path}")

            return True

        except Exception as e:
            print(f"Erreur lors de la suppression de l'hôte: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _contains_host_definition_in_text(self, text: str) -> bool:
        '''Vérifie si le texte contient une définition d'hôte'''
        return bool(re.search(r'define\s+host\s*\{', text, re.IGNORECASE))

    def _generate_host_config(self, host_data: Dict) -> str:
        '''Génère le contenu de configuration pour un hôte'''
        lines = ["define host {"]

        # Ordre des directives
        directive_order = [
            'use', 'host_name', 'alias', 'address',
            'max_check_attempts', 'check_interval', 'retry_interval',
            'check_command', 'notification_interval', 'notification_period',
            'contacts', 'contact_groups'
        ]

        # Ajouter les directives dans l'ordre
        for directive in directive_order:
            if directive in host_data and host_data[directive]:
                lines.append(f"    {directive:<30} {host_data[directive]}")

        # Ajouter les autres directives non listées
        for key, value in host_data.items():
            if key not in directive_order and key not in ['file_path', 'directory']:
                if value:
                    lines.append(f"    {key:<30} {value}")

        lines.append("}")
        lines.append("")  # Ligne vide à la fin

        return '\n'.join(lines)

    def _add_cfg_file_to_nagios_cfg(self, file_path: str):
        '''
        Ajoute un fichier de configuration à nagios.cfg si nécessaire
        '''
        try:
            with open(self.nagios_cfg, 'r') as f:
                content = f.read()

            # Vérifier si le fichier ou son répertoire est déjà référencé
            directory = os.path.dirname(file_path)

            # Vérifier cfg_dir
            if f"cfg_dir={directory}" in content:
                return  # Le répertoire est déjà inclus

            # Vérifier cfg_file
            if f"cfg_file={file_path}" in content:
                return  # Le fichier est déjà inclus

            # Ajouter une ligne cfg_file
            with open(self.nagios_cfg, 'a') as f:
                f.write(f"\ncfg_file={file_path}\n")

        except Exception as e:
            print(f"Erreur lors de l'ajout à nagios.cfg: {e}")

    def validate_configuration(self) -> tuple:
        '''
        Valide la configuration Nagios
        Retourne (success: bool, output: str)
        '''
        try:
            result = subprocess.run(
                [self.nagios_bin, '-v', self.nagios_cfg],
                capture_output=True,
                text=True,
                timeout=30
            )

            return (result.returncode == 0, result.stdout + result.stderr)

        except Exception as e:
            return (False, f"Erreur lors de la validation: {e}")

    def restart_nagios(self) -> tuple:
        '''
        Redémarre Nagios
        Retourne (success: bool, output: str)
        '''
        try:
            result = subprocess.run(
                ['systemctl', 'restart', 'nagios'],
                capture_output=True,
                text=True,
                timeout=30
            )

            return (result.returncode == 0, result.stdout + result.stderr)

        except Exception as e:
            return (False, f"Erreur lors du redémarrage: {e}")

    def get_directories(self) -> List[str]:
        '''Liste tous les sous-répertoires dans le chemin de base Nagios'''
        directories = []

        for root, dirs, files in os.walk(self.nagios_base_path):
            # Calculer le chemin relatif
            rel_path = os.path.relpath(root, self.nagios_base_path)
            if rel_path != '.':
                # Retourner le chemin absolu complet
                directories.append(root)

        return sorted(directories)
