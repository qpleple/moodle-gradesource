# -*- coding: utf-8 -*-

from termcolor import colored, cprint
from BeautifulSoup import BeautifulSoup
import requests, re

import utils

class Gradesource:
  cookies       = None
  loginUrl      = "https://www.gradesource.com/validate.asp"
  assessmentUrl = "https://www.gradesource.com/editscores1.asp?id=%s"
  courseUrl     = "https://www.gradesource.com/selectcourse.asp?id=21802"
  postScoresUrl = "https://www.gradesource.com/updatescores1.asp"
  
  def __init__(self, username, passwd):
    cprint("Logging into Gradesource with username %s" % username, 'yellow')
    
    postData = {'User' : username, 'Password' : passwd}
    response = requests.post(self.loginUrl, data = postData)
    self.cookies = response.cookies
    
    # TODO: raise an exception if login failed
  
  def parseScoresForm(self, assessmentId):
    url = self.assessmentUrl % assessmentId
    cprint("Downloading Gradesource page %s" % url, 'yellow')
    
    # dirty workaround: get the course page before 
    requests.get(self.courseUrl, cookies = self.cookies)
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