#!/usr/bin/env python
# encoding=utf8

from __future__ import print_function
import json
import time
import datetime
import argparse
import sys
reload(sys)  
sys.setdefaultencoding('utf8')

import collections
import os
import ConfigParser

import requests
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests import RequestException

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

import logging
FORMAT = "%(asctime)s %(levelname)-5.5s [%(name)s][%(threadName)s] %(message)s"
logging.basicConfig(format=FORMAT)
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)

import shutil
import subprocess
import logging
from sys import platform as _platform


k_app_name = 'buildresty'
k_settings_path = os.path.expanduser('~/.{0}'.format(k_app_name))
k_settings_file = os.path.join(k_settings_path, '{0}.ini'.format(k_app_name))
project_name_placeholder = "~~~PROJNAME~~~"
base_dir = None
abs_env_dir = None
app_root_dir = None
"""
k_settings_default_username = 'default_username'
k_settings_default_password = 'default_password'

# k_api_url_prefix = 'https://track.dcts.tdbank.com/rest/api/2/'
# k_search_param_assignee = 'search?jql=assignee='
"""
# Red = '\033[91m'
# Green = '\033[92m'
# Blue = '\033[94m'
# Cyan = '\033[96m'
# White = '\033[97m'
# Yellow = '\033[93m'
# Magenta = '\033[95m'
# Grey = '\033[90m'
# Black = '\033[90m'
# Default = '\033[99m'

k_default_prefix = '\033[99m'
k_yellow_prefix = '\033[93m'
k_blue_prefix = '\033[94m'
k_cyan_prefix = '\033[96m'
k_green_prefix = '\033[92m'
k_red_prefix = '\033[91m'
k_colourize_postfix = '\033[0m'

"""
def initialize_settings():
    if not os.path.exists(k_settings_path):
        os.makedirs(k_settings_path)

    if not os.path.exists(k_settings_file):
        parser = ConfigParser.SafeConfigParser()

        parser.add_section('user')
        parser.set('user', 'username', k_settings_default_username)
        parser.set('user', 'password', k_settings_default_password)
        with open(k_settings_file, 'w') as file:
            parser.write(file)

def user_settings():    
    parser = ConfigParser.SafeConfigParser()
    parser.read(k_settings_file)
    user_items = parser.items('user')
    return {'username': parser.get('user', 'username'), 'password': parser.get('user', 'password')}
"""

def main():
    global base_dir
    global abs_env_dir
    global settings
    """
    initialize_settings()
    user = user_settings()
    if user['username'] == k_settings_default_username or user['password'] == k_settings_default_password:
        print('Please edit your JIRA credentials at {0}'.format(k_settings_file))
        sys.exit(0)
    """

    parser = argparse.ArgumentParser(
            prog='{0}.py'.format(k_app_name),
            formatter_class=argparse.RawDescriptionHelpFormatter
            )

    subparser = parser.add_subparsers()

    build_parser = subparser.add_parser('build', description="Build a RESTy server.")
    build_parser.add_argument('-n', '--project-name', help='Name of the new pyramid project.', type=str)
    
    build_parser.add_argument('-d', '--deploy-dir', help='Deploy base directory of webapp.', type=str)
    build_parser.add_argument('-p', '--python-path', help='Path to python to use for virtualenv.', type=str)
    build_parser.set_defaults(func=buildresty)

    args = parser.parse_args()
    args.func(args)

def buildresty(args):
    global base_dir
    global abs_env_dir
    global app_root_dir
    
    base_dir = os.getcwd();
    if args.project_name is None:
        args.project_name = "default"
    if args.deploy_dir is None:
        args.deploy_dir = base_dir
    absolute_deploydir = os.path.abspath(args.deploy_dir)
    os.chdir(absolute_deploydir)

    virtualenv_cmd = None
    if args.python_path is None:
        virtualenv_cmd = ["virtualenv", args.project_name + "_env", '--no-site-packages']
    else:
        virtualenv_cmd = ["virtualenv", "--python=" + args.python_path, args.project_name + "_env", '--no-site-packages']

    subprocess.call(virtualenv_cmd)
    abs_env_dir = os.path.abspath(os.path.join(absolute_deploydir, args.project_name + "_env"))
    LOG.debug('abs_env_dir: {0}'.format(str(abs_env_dir)))
    app_root_dir = os.path.join(abs_env_dir, args.project_name)
    os.chdir(abs_env_dir)

    perform_installs(args)
    create_webapp(args)
    setup_packages(args)

def perform_installs(args):
    global abs_env_dir

    subprocess.call(['bin/pip', 'install', '-U', 'pip'])
    
    requirements = os.path.join(args.deploy_dir, "requirements.txt")
    subprocess.call(['bin/pip', 'install', '-r', requirements])
    
def create_webapp(args):
    global abs_env_dir
    
    LOG.debug('abs_env_dir: {0}'.format(str(abs_env_dir)))
    os.chdir(abs_env_dir)
    
    subprocess.call(['bin/pcreate', '-t', 'cornice', args.project_name])

def setup_packages(args):
    global app_root_dir
    
    LOG.debug('app_root_dir: {0}'.format(str(app_root_dir)))
    os.chdir(app_root_dir)

    subprocess.call(['../bin/python', 'setup.py', 'develop'])
    subprocess.call(['../bin/alembic', 'init', 'alembic'])
    
    """
    user = user_settings()
    if args.assignee is None:
        args.assignee = user['username']

    if args.include_closed is None:
        args.include_closed = False


    full_url = '{0}{1}{2}'.format(k_api_url_prefix, k_search_param_assignee, args.assignee)
    search_response_json = do_search(full_url, user['username'], user['password'])
    
    column_formatters = ['{: <15}', '{: <15}', '{: <65}', '{: <15}']
    title_final = ''
    # add the line formatters
    for formatter in column_formatters:
        title_final += formatter
 
    print(title_final.format('Key', 'Status', 'Summary', 'Priority'))

    issues = search_response_json['issues']
    for issue in issues:
        key = issue['key']
        status = issue['fields']['status']['name']
        summary = issue['fields']['summary'][0:60]
        priority = issue['fields']['priority']['name']
        
        should_print = status != 'Closed'
        
        if status == 'In Progress':
            colour_prefix = k_yellow_prefix
        elif status == 'Closed':
            colour_prefix = k_default_prefix
        elif status == 'Open':
            colour_prefix = k_cyan_prefix
        elif status == 'Resolved':
            colour_prefix = k_green_prefix
        else:
            colour_prefix = k_default_prefix
        
        
        # add main colour of line
        line_final = ''
        line_final += colour_prefix
        
        # add the line formatters
        for formatter in column_formatters:
            line_final += formatter
            
        # final step, add the colourize postfix
        line_final += k_colourize_postfix

        line_final_formatted = ''
        if isinstance(line_final_formatted, basestring):
            line_final_formatted = line_final.format(key, status, summary, priority)
        else:
            line_final_formatted = unicode(line_final.format(key, status, summary, priority))

        if should_print or args.include_closed:
            print(line_final_formatted)

def do_search(full_url, username, password):
    try:
        r = requests.get(full_url, auth=HTTPBasicAuth(username, password), params=None, verify=False)
        
        logger.info('using: ' + r.url)
        json_response = json.loads(r.text)
        return json_response
    except requests.exceptions.RequestException as e:
        # catastrophic error. bail.
        logger.error(e)
        sys.exit(1)
    except ValueError as e:
        logger.error(e)
        sys.exit(1)
    """
if __name__ == '__main__':
    main()
