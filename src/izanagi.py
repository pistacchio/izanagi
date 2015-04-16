#!/usr/bin/env python

import argparse
import datetime
import json
import imp
import os
import re
import stat
import sys
import urllib2
import tempfile
from distutils.dir_util import copy_tree

# TOP LEVEL CONSTANTS
IZANAGI_HOME               = os.path.join(os.path.expanduser("~"), '.izanagi')
IZANAGI_LOCAL_FORMULA_PATH = os.path.join(IZANAGI_HOME, 'formulas')
IZANAGI_CACHE_PATH         = os.path.join(IZANAGI_HOME, 'cache')
IZANAGI_CACHE_FILE         = os.path.join(IZANAGI_CACHE_PATH, 'cache')
IZANAGI_CONFIG_FILE        = os.path.join(IZANAGI_HOME, 'config')

GITHUB_API_BASE_URL        = 'https://api.github.com/repos/'

REGEX_FORMULA_FROM_URL     = re.compile(r'formulas/(.*?)/')

config = imp.load_source('config', IZANAGI_CONFIG_FILE)

#######################
# CLI ARGUMENT PARSER #
#######################

# TODO shortcut options like "i" for "install"
parser = argparse.ArgumentParser(prog="izanagi")
subparsers = parser.add_subparsers(dest='command', help='commands')

install_parses = subparsers.add_parser('install', help='install formula')
install_parses.add_argument('formula_name',    action='store', help='name of the formula to install', type=str)
install_parses.add_argument('destination_path', action='store', help='where to install the formula', nargs='?', type=str)
install_parses.add_argument('--opts', action='store', help='optional arguments for the installer', nargs=argparse.REMAINDER)

list_parser = subparsers.add_parser('list', help='list available formulas')

search_parser = subparsers.add_parser('search', help='search for formula')
search_parser.add_argument('search_string', action='store', help='formula to search for', type=str)

update_parser = subparsers.add_parser('update', help='update formula data from remote repositories')

args = vars(parser.parse_args())


####################
# HELPER FUNCTIONS #
####################

def get_formula(formula_name):
    formulas = {}

    if formula_name in os.listdir(IZANAGI_LOCAL_FORMULA_PATH):
        formulas['local'] = os.path.join(IZANAGI_LOCAL_FORMULA_PATH, formula_name)

    for remote_repo in json.load(open(IZANAGI_CACHE_FILE)):
        if formula_name in remote_repo['formulas']:
            formulas[remote_repo['repository']] = remote_repo['repository_url']

    return formulas


def get_remote(remote_repo_url):
    # TODO better creation of the url
    remote_api_url = GITHUB_API_BASE_URL + \
        remote_repo_url.replace('https://github.com/', '') \
        .replace('.git', '') + '/git/trees/master?recursive=1'
    response = urllib2.urlopen(remote_api_url)
    return json.loads(response.read())


def get_remote_tree(remote_repo_url):
    remote = get_remote(remote_repo_url)
    if 'tree' in remote:
        return remote['tree']
    return None


def install_formula(formula_name, destination_path, options=''):
    formulas = get_formula(formula_name)

    if formulas == {}:
        print 'Formula not found'
        sys.exit(1)

    if len(formulas) > 1:
        repositories = []
        print 'Formula found on multiple repositories:'

        # show local in first position if exists
        if 'local' in formulas:
            repositories.append('local')

        repositories += [f for f in formulas if f != 'local']

        for position, formula in enumerate(repositories):
            print '[%d] %s (%s)' % (position, formula, formulas[formula])

        while True:
            raw_origin = raw_input('Please select one: ')
            if raw_origin in [str(i) for i in range(len(repositories))]:
                origin = repositories[int(raw_origin)]
                break
            print 'Invalid choice.'
    else:
        origin = formulas.keys()[0]

    if origin == 'local':
        formula_path = formulas['local']
    else:
        def _get_repository(origin):
            repos = [r for r in json.load(open(IZANAGI_CACHE_FILE)) if r['repository'] == origin]
            if len(repos) == 0 or len(repos) > 1:
                print 'Invalid repository cache.'
                print '    Consider running "izanagi update"\n'
                sys.exit(1)
            return repos[0]

        repository = _get_repository(origin)
        all_remote_files = get_remote_tree(repository['repository_url'])
        if all_remote_files is None:
            print 'Invalid formula'
            sys.exit(1)

        # import ipdb; ipdb.set_trace()
        remote_files = [rf for rf in all_remote_files if rf['path'].startswith('formulas/' + formula_name)]
        formula_path = tempfile.mkdtemp()

        def _mkdir_recursive(path):
            sub_path = os.path.dirname(path)
            if not os.path.exists(sub_path):
                _mkdir_recursive(sub_path)
            if not os.path.exists(path):
                os.mkdir(path)

        for remote_file in remote_files:
            path = remote_file['path'].replace('formulas/' + formula_name + '/', '')
            if remote_file['mode'] == '040000':
                full_path = os.path.join(formula_path, path)
                _mkdir_recursive(full_path)
            else:
                full_path = os.path.join(formula_path, path)
                dirname = os.path.dirname(full_path)
                _mkdir_recursive(dirname)
                response = urllib2.urlopen(remote_file['url'])
                raw_content = json.loads(response.read())
                if not 'content' in raw_content:
                    print 'Error while downloading formulas'
                    os.removedirs(formula_path)
                    sys.exit(1)

                out_file = open(full_path, 'w+')
                out_file.write(raw_content['content'].decode(raw_content['encoding']))
                out_file.close()

    skel_path = os.path.join(formula_path, 'skel')
    if os.path.exists(skel_path):
        copy_tree(skel_path, destination_path)

    install_file = os.path.join(formula_path, 'install')
    if os.path.exists(install_file):
        try:
            file_stats = os.stat(install_file)
            os.chmod(install_file, file_stats.st_mode | stat.S_IEXEC)
        except:
            pass

    os.system('"%s" "%s" %s' % (install_file, destination_path, options))


def list_formulas(search_string=''):
    # show local in first position if exists
    local_formulas = os.listdir(IZANAGI_LOCAL_FORMULA_PATH)
    if search_string:
        local_formulas = [f for f in local_formulas if search_string in f]

    if local_formulas:
        print 'local (%s):' % IZANAGI_LOCAL_FORMULA_PATH
        for formula in local_formulas:
            print '    ' + formula

    for remote_repo in json.load(open(IZANAGI_CACHE_FILE)):
        remote_formulas = remote_repo['formulas']

        if search_string:
            remote_formulas = [f for f in remote_formulas if search_string in f]

        if remote_formulas:
            print '\n%s (%s):' % (remote_repo['repository'], remote_repo['repository_url'])
            for formula in remote_formulas:
                print ' '*4, formula


def search_for_formula(search_string):
    return list_formulas(search_string)


def update_cache():
    caches = []
    for remote_repo, remote_repo_url in config.remote_repos.iteritems():
        json_formulas = get_remote(remote_repo_url)
        formulas = set()

        for formula in [f['path'] for f in json_formulas['tree'] if f['path'].startswith('formulas')]:
            match = REGEX_FORMULA_FROM_URL.match(formula)
            if match:
                formulas.add(match.groups()[0])

        formulas = list(formulas)
        caches.append({
            'repository':     remote_repo,
            'repository_url': remote_repo_url,
            'updated':        str(datetime.datetime.now()),
            'formulas':       formulas
        })

    json.dump(caches, open(IZANAGI_CACHE_FILE, 'w+'))
    # print 'Already up-to-date.'
    print 'Updated.'


# ############################################################################ #
# _check_cache_status
# check if in need of update
# ############################################################################ #
def _check_cache_status(cmd):
    if cmd != 'update' and os.path.exists(IZANAGI_CACHE_FILE):
        cache = json.load(open(IZANAGI_CACHE_FILE))
        if cache:
            last_updated = cache[0]['updated']
            last_updated_d = datetime.datetime.strptime(last_updated, '%Y-%m-%d %H:%M:%S.%f')
            last_updated_diff = datetime.datetime.now() - last_updated_d
            if last_updated_diff.days > 7:
                print "WARNING - You haven't updated the repository cache in over 7 days."
                print '    Consider running "izanagi update"\n'


################
# MAIN PROGRAM #
################

if __name__ == "__main__":
    # TODO: check IZANAGI_CACHE_FILE integrity...
    _check_cache_status(args['command'])

    if args['command'] == 'list':
        list_formulas()

    if args['command'] == 'install':
        formula_name = args['formula_name']
        if args['destination_path']:
            destination_path = os.path.join(os.getcwd(), args['destination_path'])
        else:
            destination_path = os.path.join(os.getcwd(), formula_name)

        options = ' '.join(args['opts']) if args['opts'] else ''
        install_formula(formula_name, destination_path, options)

    if args['command'] == 'search':
        search_for_formula(args['search_string'])

    if args['command'] == 'update':
        update_cache()

    sys.exit(0)