""" ERGAL CLI """

import os
import sys
import time

from src.ergal.profile import Profile
from src.ergal.exceptions import ProfileException

from colorama import init; init()
from colorama import Fore, Back, Style

clear = lambda: os.system('cls' if os.name == 'nt' else 'clear')

print(Fore.CYAN, """
  _  _         |
 |/ |  /| //|  |
        |   

Welcome to ERGAL-CLI  
""")
time.sleep(1)

def main():
	""" Central CLI method.

	All local profile management can be done here.
	
	"""
	clear()
	print(Fore.CYAN, 'ERGAL-CLI : Profile Management')
	print(Fore.MAGENTA, """
	1. Create a profile.
	2. Load/edit a profile.
	3. Quit ERGAL-CLI.
	""", Fore.RESET)

	action = input('Action: ')
	if int(action) == 1:
		create()
	elif int(action) == 2:
		load()
	elif int(action) == 3:
		clear()
		sys.exit()


def create():
	""" Create a profile. """
	clear()
	print(Fore.CYAN, 'ERGAL-CLI : Profile Creation \n', Fore.RESET)

	name = input('Profile Name: ')
	base = input('Base URL: ')
	if name and base:
		try:
			profile = Profile(name, base=base)
		except ProfileException as e:
			print(Fore.RED, '\n Profile creation failed.')
			print(str(e))
		else:
			print(Fore.GREEN,
				'\n Profile for {name} created at {id}. \n'.format(
					name=profile.name,
					id=profile.id),
				Fore.RESET)
	elif name:
		profile = Profile(name)
	else:
		print(Fore.RED, 'A name for the API profile must be entered.')
		create()
	
	action = input('Press any key to return to the main menu.')
	if action or action == '':
		main()


def load():
	""" Load a profile. """
	clear()
	print(Fore.CYAN, 'ERGAL-CLI : Profile Load/Edit \n', Fore.RESET)

	name = input('Profile Name: ')
	if name:
		try:
			profile = Profile(name)
		except ProfileException as e:
			print(Fore.RED, '\n Failed to load profile.')
			print(str(e))
		else:
			print(Fore.GREEN,
				'\n {name} profile loaded. \n'.format(
					name=profile.name),
				Fore.RESET)
	else:
		print(Fore.RED, 'A name for the API profile must be entered.')
		load()


def edit():
	""" Edit a profile. """
	return 'doops'


if __name__ == '__main__': 
    try:
        main()
    except KeyboardInterrupt:
        clear()

