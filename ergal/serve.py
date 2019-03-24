"""
ergal.gui
~~~~~~~~~

This module implements the serve utility for the Ergal CLI.
"""

import os
import argparse


parser = argparse.ArgumentParser()

parser.add_argument(
    '-d', '--development',
    help='launch in development mode',
    action='store_true')
args = parser.parse_args()

if args.development:
    print('Launching Flask in development mode...')
    os.environ['FLASK_APP'] = 'ergal/gui/app.py'
    os.environ['FLASK_ENV'] = 'development'
    os.system('flask run')
else:
    print('Launching Flask...')
    os.environ['FLASK_APP'] = 'ergal/gui/app.py'

os.system('flask run --reload')