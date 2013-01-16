# -*- coding: utf-8 -*-

# install: requests, beautifulsoup4, termcolor

import re, sys, csv, pickle
from getpass import getpass
from BeautifulSoup import BeautifulSoup
from termcolor import colored, cprint

from moodle import Moodle
from gradesource import Gradesource
import utils

def passwd(service):
  data = pickle.load(open('passwd.pickle', 'rb'))
  return data[service]

def importQuiz(moodleClassID, moodleColumn, assessmentId):
  moodle = Moodle('qpleple', passwd('moodle'))
  nameToScore = moodle.quizGrades(moodleColumn, moodleClassID)
  utils.check("Moodle name -> score: ", nameToScore)

  gradesource = Gradesource('qpleple20', passwd('gradesource'))
  gradesource.importScores(nameToScore, assessmentId)

def importParticipation(gradesource, assessmentId, date):
  filename = "participation/participation-%s.txt" % date
  cprint('Reading names from file %s' % filename, 'yellow')
  names = eval(open(filename).read())
  
  nameToScore = dict([(name, 1) for name in names])
  utils.check("Nname to score: ", nameToScore)
  
  gradesource = Gradesource('qpleple20', passwd('gradesource'))
  gradesource.importScores(nameToScore, assessmentId)

def importClickerScores(csvPath, col, assessmentId):
  g = Gradesource('qpleple20', passwd('gradesource'))
  reader = csv.reader(open(csvPath, 'rU'), delimiter=',')
  scores = dict([(row[0] + ' ' + row[1], row[col]) for row in list(reader)])
  g.importScores(scores, assessmentId)

# Examples:
# importQuiz(moodleClassID = 175, moodleColumn = 7, assessmentId = 420003)
# importParticipation('11-03-01', 416781)
# importClickerScores("/Users/qt/Desktop/shachar.csv", 420003)
