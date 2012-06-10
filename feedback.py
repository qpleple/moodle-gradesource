# -*- coding: utf-8 -*-

from moodle import Moodle
from gradesource import Gradesource
import utils
from termcolor import colored, cprint
from getpass import getpass
import pickle
import smtplib
import random

def getFeedback(reportId, column):
  gradesource = Gradesource('quentin', getpass('Gradesource password: '))
  emails = gradesource.emails()
  utils.check('Emails', emails)

  moodle = Moodle('qpleple', getpass('Moodle password: '))
  feedback = moodle.quizFeedback(reportId, column)
  utils.check('Feedback', feedback)
  
  GSnames = gradesource.matchNames(feedback.keys(), emails.keys())
  
  data = {}
  for name, content in feedback.items():
    # print '%s %s %s' % (name, colored(email, 'blue'), colored(content, 'green'))
    # answer = raw_input()
    data[name] = {
      'email': emails[GSnames[name]],
      'feedback': content,
    }
    
  utils.check('Feedback', data)
  
  return data

def writeAnwers(feedback):
  n = len(feedback.items())
  for i, (name, doc) in enumerate(feedback.items()):
    fraction = "%s/%s" % (i, n)
    print '%s %s %s %s' % (colored(fraction, 'blue'), name, colored(doc['email'], 'blue'), colored(doc['feedback'], 'green'))
    if 'answer' in feedback[name] and feedback[name]['answer'].strip() :
      cprint(feedback[name]['answer'], 'red')
    else:
      answer = raw_input().strip()
      if answer == 'stop':
        break
      if answer.strip():
        feedback[name]['answer'] = answer
  pickle.dump(feedback, open('feedback-answers.pickle', 'wb'))

# writeAnwers(pickle.load(open('feedback-answers.pickle')))
# blacklist = []

def emailAnswers(feedback, blacklist = []):
  passwd = getpass('Gmail password: ')
  do = True
  for name, doc in feedback.items():
    print colored(name, 'yellow')
    if not do or name in blacklist:
      print colored('Blacklisted', 'red')
      if name == 'Bla bla':
        do = True
      continue
    if not 'answer' in doc or not doc['answer'].strip():
      continue
    msg = doc['answer']
    nl = '<br>\n'
    msg += nl + nl + "Quentin"
    msg += nl + nl + "%s wrote in Moodle Quiz:" % name
    msg += nl + "> " + doc['feedback']
    print 'Sending to %s <%s>:\n%s' % (name, doc['email'], colored(msg, 'blue'))
    sendEmailFeedback(doc['email'], name, msg, passwd)
    
def sendEmailFeedback(to, name, msg, passwd):
  subject = "Your Feedback #%s" % int(random.random() * 10000)
  sender  = "qpleple@ucsd.edu"
  body    = '' + msg.encode('utf8', 'ignore').decode('utf8', 'ignore').encode('ascii', 'ignore') + ''
  headers = ["From: Quentin Pleple <%s>" % sender,
             "Subject: " + subject,
             "To: %s <%s>" % (name, to),
             "MIME-Version: 1.0",
             "Content-Type: text/html"]
  headers = "\r\n".join(headers)
  
  session = smtplib.SMTP('smtp.gmail.com', 587)
  session.ehlo()
  session.starttls()
  session.ehlo
  session.login('quentin.pleple@gmail.com', passwd)
  session.sendmail(sender, to, headers + "\r\n\r\n" + body)
