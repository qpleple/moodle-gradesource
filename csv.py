# -*- coding: utf-8 -*-

import re, sys, csv, pickle
from termcolor import colored, cprint
from gradesource import Gradesource
import utils

# Read the CSV files for grades
csvPath = sys.argv[1]
lines = list(csv.reader(open(csvPath, 'rU'), delimiter = ','))
first_line = lines[0]
# ignore 1st line and lines starting by '#' (unregistered clickers)
lines = [l for l in lines[1:] if l[0][0] != '#']

# Ask for the column to pick in theh file
for col, title in enumerate(first_line):
  print colored(col, 'green') + ' ' + title
pid_col   = int(raw_input(colored('PID column ? ', 'green')))
score_col = int(raw_input(colored('Score column ? ', 'green')))

# Keep only lines with non-zero score
lines = [l for l in lines if l[score_col] not in [0, '0', '-', '']]
data  = [{'score': l[score_col], 'pid': l[pid_col]} for l in lines]

# Ask for the assessment to upload the grade
config = utils.getConfig()
g = Gradesource(config['gradesourceLogin'], config['gradesourcePasswd'])
g.importScoresBy(data, 'pid')