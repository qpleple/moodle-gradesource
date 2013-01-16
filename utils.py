# -*- coding: utf-8 -*-

from termcolor import colored, cprint
import pickle

def editDist(s1, s2):
    d = {}
    lenstr1 = len(s1)
    lenstr2 = len(s2)
    for i in xrange(-1,lenstr1+1):
        d[(i,-1)] = i+1
    for j in xrange(-1,lenstr2+1):
        d[(-1,j)] = j+1

    for i in xrange(lenstr1):
        for j in xrange(lenstr2):
            if s1[i] == s2[j]:
                cost = 0
            else:
                cost = 1
            d[(i,j)] = min(
                           d[(i-1,j)] + 1, # deletion
                           d[(i,j-1)] + 1, # insertion
                           d[(i-1,j-1)] + cost, # substitution
                          )
            if i and j and s1[i]==s2[j-1] and s1[i-1] == s2[j]:
                d[(i,j)] = min (d[(i,j)], d[i-2,j-2] + cost) # transposition

    return d[lenstr1-1,lenstr2-1]

def powerset(s):
    n = len(s)
    masks = [1<<j for j in xrange(n)]
    for i in xrange(2**n):
        yield [s[j] for j in range(n) if (masks[j] & i)]
        
def check(label, toDisplay):
  print colored(label, 'yellow') + str(toDisplay)
  raw_input(colored('continue ? ', 'green'))

def setConfig():
  config = {}
  config['moodleCourseId']    = int(raw_input('Moodle class id: '))
  config['moodleLogin']       = raw_input('Moodle login: ')
  config['moodlePasswd']      = raw_input('Moodle password: ')
  config['gradesourceLogin']  = raw_input('Gradesource login: ')
  config['gradesourcePasswd'] = raw_input('Gradeource password: ')

  pickle.dump(config, open('config.pickle', 'wb'))
  cprint('Saved!', 'green')

def getConfig():
  return pickle.load(open('config.pickle', 'rb'))