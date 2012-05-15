# -*- coding: utf-8 -*-

# install: requests, beautifulsoup4, termcolor

import re, sys
from getpass import getpass
from BeautifulSoup import BeautifulSoup
from termcolor import colored, cprint

from moodle import Moodle
from gradesource import Gradesource
import utils

def importQuiz(moodleClassID, moodleColumn, assessmentId):
  moodle = Moodle('qpleple', getpass(), moodleClassID)
  nameToScore = moodle.quizGrades(moodleColumn)
  utils.check("Moodle name -> score: ", nameToScore)

  gradesource = Gradesource('quentin', getpass())
  gradesource.importScores(nameToScore, assessmentId)

def importParticipation(gradesource, assessmentId, date):
  filename = "participation/participation-%s.txt" % date
  cprint('Reading names from file %s' % filename, 'yellow')
  names = eval(open(filename).read())
  
  nameToScore = dict([(name, 1) for name in names])
  utils.check("Nname to score: ", nameToScore)
  
  gradesource = Gradesource('qpleple1', getpass())
  gradesource.importScores(nameToScore, assessmentId)
  

# moodle = Moodle('qpleple', getpass(), 155)
# nameToScore = moodle.quizGrades(9)

importQuiz(175, 5, 420001)
# importParticipation('11-03-01', 416781)