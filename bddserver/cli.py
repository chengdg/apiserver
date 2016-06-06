# -*- coding: utf-8 -*-
import sys
import argparse
import os


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('action')
	args = parser.parse_args()

	action = args.action

	print('sys.argv[0]', sys.argv[0])

	print('os.getcwd', os.getcwd())
	print('os.path.abspath', os.path.abspath(os.curdir))

	print("---action:", action)


if __name__ == "__main__":
	main()
