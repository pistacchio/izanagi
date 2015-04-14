#!/usr/bin/env python

import argparse
import os
import stat
import sys

from distutils.dir_util import copy_tree

# TOP LEVEL CONSTANTS
IZANAGI_HOME               = os.path.join(os.path.expanduser("~"), '.izanagi')
IZANAGI_LOCAL_FORMULA_PATH = os.path.join(IZANAGI_HOME, 'formulas')

# CLI ARGUMENT PARSER
parser     = argparse.ArgumentParser(prog="izanagi")
subparsers = parser.add_subparsers(dest='command', help='commands')

install_parses = subparsers.add_parser('install', help='install formula')
install_parses.add_argument('formula_name',    action='store', help='name of the formula to install', type=str)
install_parses.add_argument('destination_path', action='store', help='where to install the formula', nargs='?', type=str)
install_parses.add_argument('--opts', action='store', help='optional arguments for the installer', nargs=argparse.REMAINDER)

list_parser = subparsers.add_parser('list', help='list available formulas')

search_parser = subparsers.add_parser('search', help='search for formula')
search_parser.add_argument('search_string',    action='store', help='formula to search for', type=str)

args = vars(parser.parse_args())

# HELPER FUNCTIONS

def get_local_formula(formula_name):
    if formula_name in os.listdir(IZANAGI_LOCAL_FORMULA_PATH):
        return os.path.join(IZANAGI_LOCAL_FORMULA_PATH, formula_name)

def get_formula(formula_name):
    return get_local_formula(formula_name)

def list_formulas():
    for formula in os.listdir(IZANAGI_LOCAL_FORMULA_PATH):
        print formula

def search_for_formula(search_string):
    for formula in [f for f in os.listdir(IZANAGI_LOCAL_FORMULA_PATH) if search_string in f]:
        print formula


# MAIN PROGRAM
if __name__ == "__main__":
    if args['command'] == 'list':
        list_formulas()
        sys.exit(0)

    if args['command'] == 'install':
        formula_name = args['formula_name']
        formula_path = get_formula(formula_name)

        if not formula_path:
            print 'Formula not found'
            sys.exit(1)

        if args['destination_path']:
            destination_path = os.path.join(os.getcwd(), args['destination_path'])
        else:
            destination_path = os.path.join(os.getcwd(), formula_name)

        skel_dir = os.path.join(formula_path, 'skel')
        if os.path.exists(skel_dir):
            copy_tree(skel_dir, destination_path)

        install_file = os.path.join(formula_path, 'install')
        if os.path.exists(install_file):
            try:
                file_stats = os.stat(install_file)
                os.chmod(install_file, file_stats.st_mode | stat.S_IEXEC)
            except:
                pass

        options = ' '.join(args['opts']) if args['opts'] else ''
        os.system('"%s" "%s" %s' % (install_file, destination_path, options))
        sys.exit(0)

    if args['command'] == 'search':
        search_for_formula(args['search_string'])
        sys.exit(0)
