# -*- coding: utf-8 -*-

from termcolor import colored, cprint
from BeautifulSoup import BeautifulSoup
import requests, re, sys

import utils

class Gradesource:
  cookies       = None
  rootUrl       = "https://www.gradesource.com"
  loginUrl      = rootUrl + "/validate.asp"
  assessmentUrl = rootUrl + "/editscores1.asp?id=%s"
  postScoresUrl = rootUrl + "/updatescores1.asp"
  studentsUrl   = rootUrl + "/student.asp"
  
  def __init__(self, username, passwd):
    cprint("Logging into Gradesource with username %s" % username, 'yellow')
    
    postData = {'User' : username, 'Password' : passwd}
    response = requests.post(self.loginUrl, data = postData)
    self.cookies = response.cookies
    
    if response.status_code == 302:
      location = response.headers['location']
      if location == 'login.asp':
        print colored(' Wrong login/password ', 'white', 'on_red')
        sys.exit()
      else:
        requests.get(self.rootUrl + '/' + location, cookies = self.cookies)

  def parseScoresForm(self, assessmentId):
    url = self.assessmentUrl % assessmentId
    cprint("Downloading Gradesource page %s" % url, 'yellow')
    
    html = requests.get(url, cookies = self.cookies).content

    cprint("Parsing the form page HTML", 'yellow')
    soup = BeautifulSoup(html)
    nameToStudentId = {}
    postData = {}

    for x in soup.form('input', id = re.compile("^student")):
      name = x.parent.parent.contents[1].string.strip("&nbsp;")
      td = x.parent.contents[1]
      postData[td['name']] = td['value']
      nameToStudentId[name] = x['id']
    
    postData.update({
      'assessmentId' : assessmentId,
      'studentCount' : len(nameToStudentId),
    })
    
    return nameToStudentId, postData
  
  def matchNames(self, externalNames, GsNames):
    """Returns a dictionnary: External name -> Gradesource name"""
    cprint('Matching students', 'yellow')
    mapping = {}
    
    # externalDict: "alphonse blah jean" -> "Jean-Alphonse Blah"
    externalDict = {}
    for n in externalNames:
      subNames = n
      subNames = subNames.replace('-', ' ').replace(',', ' ').lower().split(' ')
      subNames.sort()
      externalDict[" ".join(subNames)] = n
  
    # GsDict:
    # "alphonse blah jean",
    # "blah jean",
    # "alphonse jean",
    # "alphonse blah",
    # -> "Jean-Alphonse Blah"
    GsDict = {}
    for n in GsNames:
      subNames = n
      subNames = subNames.replace('-', ' ').replace(',', ' ').lower().split(' ')
      # only keep more-than-one-letter subnames 
      subNames = [x for x in subNames if len(x) > 1]
      subNames.sort()
      # include all possibility
      for possibility in utils.powerset(subNames):
        if len(possibility) > 1:
          GsDict[" ".join(possibility)] = n
  
    format = "%3s %25s - %-25s (%s)"
    cprint(format % ("#", "External name", "Gradesource name", "distance"), 'yellow')
    for i, externalCleaned in enumerate(externalDict):
      dist, GsCleaned = min([(utils.editDist(externalCleaned, x), x) for x in GsDict.keys()])
      if dist == 0:
        color = 'white'
      elif dist <= 2:
        color = 'yellow'
      else:
        color = 'red'
      cprint(format % (i + 1, externalCleaned, GsCleaned, str(dist)), color)
      mapping[externalDict[externalCleaned]] = GsDict[GsCleaned]
      
      for possibility in utils.powerset(GsCleaned.split(' ')):
        if len(possibility) > 1:
          del GsDict[' '.join(possibility)]
    return mapping
  
  def postScores(self, postData):
    cprint("Posting data", 'yellow')
    requests.post(self.postScoresUrl, data = postData, cookies = self.cookies)
    
  def importScores(self, scores, assessmentId):
    GsNameToStudentId, postData = self.parseScoresForm(assessmentId)
    utils.check("Gradesource name -> studentId: ", GsNameToStudentId)
  
    ExtNameToGsName = self.matchNames(scores.keys(), GsNameToStudentId.keys())
  
    for extName, GsName in ExtNameToGsName.items():
      postData[GsNameToStudentId[GsName]] = scores[extName]
    utils.check("Data to post: ", postData)
  
    self.postScores(postData)
    cprint("Go to %s" % (self.assessmentUrl % assessmentId), 'yellow')
  
  def emails(self):
    cprint("Downloading Gradesource page %s" % self.studentsUrl, 'yellow')
    html = requests.get(self.studentsUrl, cookies = self.cookies).content

    emails = {}

    cprint("Parsing the page", 'yellow')
    soup = BeautifulSoup(html)
    tbody = soup('td', text=re.compile("Secret*"))[0].parent.parent.parent.parent
    for tr in tbody('tr'):
      try:
        name  = tr.contents[1].text.strip()
        email = tr.contents[7].text.strip()
        emails[name] = email
      except Exception, e:
        continue
    return emails
    
