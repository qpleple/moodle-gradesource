# -*- coding: utf-8 -*-

# install: requests, beautifulsoup4, termcolor

import re, sys, csv, pickle
from getpass import getpass
from BeautifulSoup import BeautifulSoup
from termcolor import colored, cprint

from moodle import Moodle
from gradesource import Gradesource
import utils

def uploadMoodleQuizScores():
  config = utils.getConfig()

  m = Moodle(config['moodleLogin'], config['moodlePasswd'])
  _, scores = m.getScores(config['moodleCourseId'])
  # Fields: 0:FN, 1:LN, 2:pid, 3:inst, 4:dpt, 5:email, 6:total, 7:score
  data = [{'name': '%s, %s' % (row[1], row[0]), 'score': row[7], 'pid': row[2], 'email': row[5]} for row in scores if row[7] not in [0, '0', '-', '']]
  
  utils.check("Moodle data: ", data)

  g = Gradesource(config['gradesourceLogin'], config['gradesourcePasswd'])
  g.importScoresBy(data, 'pid')

def uploadClickerScores(csvPath, col):
  config = utils.getConfig()

  reader = csv.reader(open(csvPath, 'rU'), delimiter=',')
  # Fields: 0:LN, 1:FN, 2:id, >2:scores
  data = [{'name': '%s, %s' % (row[0], row[1]), 'score': row[col], 'pid': row[2]} for row in reader if row[col] not in [0, '0', '-', '']]
  utils.check("Clicker data: ", data)

  g = Gradesource(config['gradesourceLogin'], config['gradesourcePasswd'])
  g.importScoresBy(data, 'pid')

def temp(csvPath, col):
  config = utils.getConfig()
  reader = csv.reader(open(csvPath, 'rU'), delimiter=',')
  data = [{'name': "{0[0]}, {0[1]}".format(row), 'score': row[col], 'pid': row[2]} for row in reader if row[col] not in [0, '0', '-', '']]
  utils.check("Data: ", data)

  g = Gradesource(config['gradesourceLogin'], config['gradesourcePasswd'])
  g.importScoresBy(data, 'pid')


# Examples:
# utils.setConfig()
# uploadMoodleQuizScores()
# uploadClickerScores("/Users/qt/Desktop/shachar.csv", 4)

