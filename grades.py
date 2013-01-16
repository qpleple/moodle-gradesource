# -*- coding: utf-8 -*-

# install: requests, beautifulsoup4, termcolor

import re, sys, csv, pickle
from getpass import getpass
from BeautifulSoup import BeautifulSoup
from termcolor import colored, cprint

from moodle import Moodle
from gradesource import Gradesource
import utils

def importQuiz():
  config = utils.getConfig()

  m = Moodle(config['moodleLogin'], config['moodlePasswd'])
  _, scores = m.getScores(config['moodleCourseId'])
  # Fields: 0:FN, 1:LN, 2:id, 3:inst, 4:dpt, 5:email, 6:total, 7:score
  emailsToScore = dict([(row[5], {'score': row[7], 'name': '%s, %s' % (row[1], row[0])}) for row in scores])
  utils.check("Moodle name -> score: ", emailsToScore)

  g = Gradesource(config['gradesourceLogin'], config['gradesourcePasswd'])
  g.importScoresByEmails(emailsToScore)

def importParticipation(date):
  config = utils.getConfig()

  filename = "participation/participation-%s.txt" % date
  cprint('Reading names from file %s' % filename, 'yellow')
  names = eval(open(filename).read())
  
  nameToScore = dict([(name, 1) for name in names])
  utils.check("Nname to score: ", nameToScore)
  
  g = Gradesource(config['gradesourceLogin'], config['gradesourcePasswd'])
  g.importScoresByNames(nameToScore)

def importClickerScores(csvPath, col):
  config = utils.getConfig()

  reader = csv.reader(open(csvPath, 'rU'), delimiter=',')
  # Fields: 0:LN, 1:FN, 2:id, >2:scores
  nameToScore = dict([(row[0] + ' ' + row[1], row[col]) for row in list(reader)])
  utils.check("Clicker name -> score: ", nameToScore)

  g = Gradesource(config['gradesourceLogin'], config['gradesourcePasswd'])
  g.importScoresByNames(nameToScore)

# Examples:
# utils.setConfig()
# importQuiz()
# importParticipation('11-03-01')
# importClickerScores("/Users/qt/Desktop/shachar.csv", 2)