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
FORMAT = '%(asctime)s %(levelname)-5.5s [%(name)s][%(threadName)s] %(message)s'
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
project_name_placeholder = '~~~PROJNAME~~~'
script_name_placeholder = '~~~SCRIPTNAME~~~'
script_dir = None
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
    global script_dir
    
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

    build_parser = subparser.add_parser('build', description='Build a RESTy server.')
    build_parser.add_argument('-n', '--project-name', help='Name of the new pyramid project.', type=str)
    
    build_parser.add_argument('-d', '--deploy-dir', help='Deploy base directory of webapp.', type=str)
    build_parser.add_argument('-p', '--python-path', help='Path to python to use for virtualenv.', type=str)
    build_parser.add_argument('-m', '--migrations', help='Use alembic for database migrations. `sqlite` or `postgresql` Default is sqlite. If flag is missing, do not deploy database code at all.', type=str)

    build_parser.set_defaults(func=buildresty)
    args = parser.parse_args()
    LOG.debug('args: {0}'.format(str(args)))
    script_dir = os.path.dirname(os.path.realpath(__file__))
    LOG.debug('script_dir: {0}'.format(str(script_dir)))

    args.func(args)

def buildresty(args):
    global base_dir
    global abs_env_dir
    global app_root_dir
    
    base_dir = os.getcwd();
    if args.project_name is None:
        args.project_name = 'default'
    if args.deploy_dir is None:
        args.deploy_dir = base_dir

    absolute_deploydir = os.path.abspath(args.deploy_dir)
    os.chdir(absolute_deploydir)

    virtualenv_cmd = None
    if args.python_path is None:
        virtualenv_cmd = ['virtualenv', args.project_name + '_env', '--no-site-packages']
    else:
        virtualenv_cmd = ['virtualenv', '--python=' + args.python_path, args.project_name + '_env', '--no-site-packages']

    subprocess.call(virtualenv_cmd)
    abs_env_dir = os.path.abspath(os.path.join(absolute_deploydir, args.project_name + '_env'))
    LOG.debug('abs_env_dir: {0}'.format(str(abs_env_dir)))
    app_root_dir = os.path.join(abs_env_dir, args.project_name)
    os.chdir(abs_env_dir)

    perform_installs(args)
    create_webapp(args)
    setup_packages(args)
    if args.migrations is not None:
        setup_migrations(args)
    subprocess.call(['../bin/python', 'setup.py', 'develop'])

    if args.migrations is not None:
        ''' alembic autogenerate and upgrade to head to generate the trivial tasks db ''' 
        subprocess.call(['../bin/alembic', '-c', '{args.project_name}.ini'.format(**locals()), 'revision', '--autogenerate', '-m', '\'initializedb\''])
        subprocess.call(['../bin/alembic', '-c', '{args.project_name}.ini'.format(**locals()), 'upgrade', 'head'])


def perform_installs(args):
    global abs_env_dir
    global base_dir

    subprocess.call(['bin/pip', 'install', '-U', 'pip'])
    
    requirements = os.path.join(base_dir, 'requirements.txt')
    LOG.debug('requirements: {0}'.format(str(requirements)))
    subprocess.call(['bin/pip', 'install', '-r', requirements])

    if args.migrations == 'postgresql':
        subprocess.call(['bin/pip', 'install','alembic'])
        subprocess.call(['bin/pip', 'install','psycopg2'])
    elif args.migrations == 'sqlite':
        subprocess.call(['bin/pip', 'install','alembic'])
        
def create_webapp(args):
    global abs_env_dir
    
    LOG.debug('abs_env_dir: {0}'.format(str(abs_env_dir)))
    os.chdir(abs_env_dir)
    
    subprocess.call(['bin/pcreate', '-t', 'cornice', args.project_name])

def setup_packages(args):
    global app_root_dir
    
    LOG.debug('app_root_dir: {0}'.format(str(app_root_dir)))
    os.chdir(app_root_dir)

#     subprocess.call(['../bin/python', 'setup.py', 'develop'])
    subprocess.call(['../bin/alembic', 'init', 'alembic'])


def setup_migrations(args):
    global app_root_dir
    global k_app_name
    global script_dir

    os.chdir(app_root_dir)
    LOG.debug('app_root_dir: {0}'.format(str(app_root_dir)))
    app_src_dir = os.path.join(app_root_dir,'{args.project_name}'.format(**locals()))

    inserted_notice_begin = '### BEGIN inserted by {0} ###\n'.format(k_app_name)
    inserted_notice_end = '\n### END inserted by {0} ###\n'.format(k_app_name)
    
    appini = os.path.join(app_root_dir, '{0}.ini'.format(args.project_name))
    appinitpy = os.path.join(app_src_dir, '__init__.py')
    setuppy = os.path.join(app_root_dir, 'setup.py')
    alembic_envpy = os.path.join(app_root_dir, 'alembic/env.py')

    ''' update .ini file '''
    substitute_in_file(appini, 'pyramid.default_locale_name = en', '{inserted_notice_begin}pyramid.default_locale_name = en\npyramid.includes = pyramid_tm{inserted_notice_end}'.format(**locals()))

    pg_comment_out = '# ' if args.migrations == 'sqlite' else ''
    sl_comment_out = '# ' if args.migrations == 'postgresql' else ''

    postgres_url = '{pg_comment_out}sqlalchemy.url = postgresql+psycopg2://PGUSERNAME:PGPASSWORD@localhost/{args.project_name}'.format(**locals())
    sqlite_url = '{sl_comment_out}sqlalchemy.url = sqlite:///%(here)s/{args.project_name}.sqlite'.format(**locals())

    substitute_in_file(appini, '[server:main]', '{inserted_notice_begin}{postgres_url}\n{sqlite_url}\n\n[server:main]{inserted_notice_end}'.format(**locals()))
    
    alembic_chunk = '[alembic]\nscript_location = alembic'

    substitute_in_file(appini, 'port = 6543', '{inserted_notice_begin}port = 6543\n\n{alembic_chunk}{inserted_notice_end}'.format(**locals()))
#port = 6543

    ''' update setup.py file '''
    substitute_in_file(setuppy, '      install_requires=[\'cornice\', \'waitress\'],', '{inserted_notice_begin}      install_requires=[\'cornice\', \'pyramid_tm\', \'waitress\'],{inserted_notice_end}'.format(**locals()))

    ''' update alembic/env.py file '''
    connectable_depr = '''    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool)'''
        
#     substitute_in_file(alembic_envpy, '    connectable = engine_from_config(', '#    connectable = engine_from_config(')

    connectable = '    connectable = engine_from_config(config.get_section(\'app:main\'), \'sqlalchemy.\', poolclass=pool.NullPool)'

    substitute_in_file(alembic_envpy, connectable_depr, '{inserted_notice_begin}{connectable}{inserted_notice_end}'.format(**locals()))
    
    base_import = 'from {args.project_name}.models import Base\ntarget_metadata = Base.metadata'.format(**locals())

    substitute_in_file(alembic_envpy, 'target_metadata = None', '{inserted_notice_begin}{base_import}{inserted_notice_end}'.format(**locals()))
    
    ''' update main __init__.py '''
    from_pyramid = 'from pyramid.config import Configurator'
    from_pyramid_sqlalchemy = '{from_pyramid}\nfrom sqlalchemy import engine_from_config\nfrom ~~~PROJNAME~~~.models import DBSession\n\n'.format(**locals())

    def_main = 'def main(global_config, **settings):'
    def_main_engine = '{def_main}\n    engine = engine_from_config(settings, \'sqlalchemy.\')\n    DBSession.configure(bind=engine)\n'.format(**locals())
    
    substitute_in_file(appinitpy, from_pyramid, '{inserted_notice_begin}{from_pyramid_sqlalchemy}{inserted_notice_end}'.format(**locals()))
    substitute_in_file(appinitpy, def_main, '{inserted_notice_begin}{def_main_engine}{inserted_notice_end}'.format(**locals()))
    substitute_in_file(appinitpy, "~~~PROJNAME~~~", args.project_name)

    ''' copy files '''    
#     copy_src = '/Users/maz/src/buildresty/views.py'
#     copy_dest = '/Users/maz/src/buildresty/default_env/default/default/views.py'
    copy_src = os.path.join(script_dir, 'views.py')
    copy_dest = os.path.join(app_src_dir, 'views.py')
    os.unlink(copy_dest)

    LOG.debug('copy_src: {0}'.format(str(copy_src)))
    LOG.debug('copy_dest: {0}'.format(str(copy_dest)))
    shutil.copy(copy_src, copy_dest)
    substitute_in_file(copy_dest, "~~~PROJNAME~~~", args.project_name)
    substitute_in_file(copy_dest, "~~~SCRIPTNAME~~~", k_app_name)

    models_dir = os.path.join(app_src_dir, 'models')
    os.mkdir(models_dir)
    
    copy_src = os.path.join(script_dir, 'models__init__.py')
    copy_dest = os.path.join(models_dir, '__init__.py')
    LOG.debug('copy_src: {0}'.format(str(copy_src)))
    LOG.debug('copy_dest: {0}'.format(str(copy_dest)))
    shutil.copy(copy_src, copy_dest)
    substitute_in_file(copy_dest, "~~~PROJNAME~~~", args.project_name)
    substitute_in_file(copy_dest, "~~~SCRIPTNAME~~~", k_app_name)

    copy_src = os.path.join(script_dir, 'modelstask.py')
    copy_dest = os.path.join(models_dir, 'task.py')
    LOG.debug('copy_src: {0}'.format(str(copy_src)))
    LOG.debug('copy_dest: {0}'.format(str(copy_dest)))
    shutil.copy(copy_src, copy_dest)
    substitute_in_file(copy_dest, "~~~PROJNAME~~~", args.project_name)
    substitute_in_file(copy_dest, "~~~SCRIPTNAME~~~", k_app_name)
        
def substitute_in_file(filename, old_string, new_string):
    s=open(filename).read()
    if old_string in s:
            LOG.info('Changing "{old_string}" to "{new_string}" in "{filename}"'.format(**locals()))
            s=s.replace(old_string, new_string)
            f=open(filename, 'w')
            f.write(s)
            f.flush()
            f.close()
    else:
            LOG.info('No occurences of "{old_string}" found in "{filename}" '.format(**locals()))


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
