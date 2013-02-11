# -*- coding: utf-8 -*-

from termcolor import colored, cprint
from BeautifulSoup import BeautifulSoup
import requests, re, sys

import utils

class Gradesource:
  cookies        = None
  rootUrl        = "https://www.gradesource.com"
  loginUrl       = rootUrl + "/validate.asp"
  assessmentUrl  = rootUrl + "/editscores1.asp?id=%s"
  postScoresUrl  = rootUrl + "/updatescores1.asp"
  studentsUrl    = rootUrl + "/student.asp"
  assessmentsUrl = rootUrl + "/assessment.asp"
  
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
      name = x.parent.parent.contents[1].string.replace("&nbsp;", "")
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
      externalDict[" ".join(subNames).strip()] = n
  
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
      if externalCleaned in GsDict:
        dist = 0
        GsCleaned = externalCleaned
      else:
        dist, GsCleaned = min([(utils.editDist(externalCleaned, x), x) for x in GsDict.keys()])

      if dist == 0:
        mapping[externalDict[externalCleaned]] = GsDict[GsCleaned]
        
        for possibility in utils.powerset(GsCleaned.split(' ')):
          if len(possibility) > 1:
            del GsDict[' '.join(possibility)]

      if dist == 0:
        color = 'white'
      else:
        color = 'red'

      cprint(format % (i + 1, externalCleaned, GsCleaned, str(dist)), color)
    return mapping
  
  def postScores(self, postData):
    cprint("Posting data", 'yellow')
    requests.post(self.postScoresUrl, data = postData, cookies = self.cookies)
    
  def importScoresByNames(self, scores, assessmentId = 0, exactGradesourceNames = False):
    if assessmentId == 0:
      assessmentId = self.chooseAssessment()

    GsNameToStudentId, postData = self.parseScoresForm(assessmentId)
    utils.check("Gradesource name -> studentId: ", GsNameToStudentId)
    
    errors = False
    if not exactGradesourceNames:
      ExtNameToGsName = self.matchNames(scores.keys(), GsNameToStudentId.keys())
  
      for extName, GsName in ExtNameToGsName.items():
        postData[GsNameToStudentId[GsName]] = scores[extName]
    else:
      for GsName, score in scores.items():
        if GsName in GsNameToStudentId:
          postData[GsNameToStudentId[GsName]] = score
        else:
          cprint('Missing name: ' + GsName, 'white', 'on_red')
          errors = True
    if errors:
      sys.exit()
    utils.check("Data to post: ", postData)
  
    self.postScores(postData)
    cprint("Go to %s" % (self.assessmentUrl % assessmentId), 'yellow')

  def importScoresBy(self, data, key):
    """
    data should be a list of dictionnaries with at least key 'score' and another one
    [{'name': 'Quentin Pleple', 'pid': 'A53010752', 'score': '10', ...}, ...]
    and key should be in ['name', 'email', 'pid']
    """
    if key not in ['name', 'email', 'pid']:
      cprint('Bad key: ' + key, 'white', 'on_red')
      sys.exit()

    assessmentId = self.chooseAssessment()
    nameToStudentId, postData = self.parseScoresForm(assessmentId)
    utils.check("Gradesource name -> studentId: ", nameToStudentId)
    
    # infos = ['Pleple, Quentin': {'email': 'qpleple@ucsd.edu', 'pid': 'A53010752'}, ...]
    # identification = {
    # 'pleple, quentin':  'Pleple, Quentin',
    # 'qpleple@ucsd.edu': 'Pleple, Quentin',
    # 'a53010752':        'Pleple, Quentin',
    # ...}
    identification = {}
    for name, infos in self.studentsInfo().items():
      identification[name.lower()] = name
      identification[infos['email'].lower()] = name
      identification[infos['pid'].lower()] = name

    errors = False
    for row in data:
      needle = row[key].lower().strip()
      if needle not in identification:
        cprint("Couldn't find: %s (%s)" % (row[key], row) , 'white', 'on_red')
        errors = True
        continue
      
      name = identification[needle]

      if name not in nameToStudentId:
        cprint('Missing name in Gradesource assessment form: ' + name, 'white', 'on_red')
        errors = True

      postData[nameToStudentId[name]] = row['score']

    if errors:
      raw_input(colored('Found some errors, continue anyway ? ', 'green'))      

    utils.check("Data to post: ", postData)
  
    self.postScores(postData)
    cprint("Go to %s" % (self.assessmentUrl % assessmentId), 'yellow')
  
  def studentsInfo(self):
    """
    Return format:
    ['Pleple, Quentin': {'email': 'qpleple@ucsd.edu', 'pid': 'A53010752'}, ...]
    """
    cprint("Downloading Gradesource page %s" % self.studentsUrl, 'yellow')
    html = requests.get(self.studentsUrl, cookies = self.cookies).content

    infos = {}

    cprint("Parsing the page", 'yellow')
    soup = BeautifulSoup(html)
    tbody = soup('td', text=re.compile("Secret*"))[0].parent.parent.parent.parent.parent
    for tr in tbody('tr')[2:-1]:
      name  = tr.contents[1].text.strip()
      pid   = tr.contents[3].text.strip()
      email = tr.contents[7].text.strip()
      if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        continue
      
      infos[name] = {'email': email, 'pid': pid}

    return infos

  def getAssessments(self):
    cprint("Downloading Gradesource page %s" % self.assessmentsUrl, 'yellow')
    html = requests.get(self.assessmentsUrl, cookies = self.cookies).content

    cprint("Parsing the page", 'yellow')
    soup = BeautifulSoup(html)
    table = soup('td', {'class': 'T'})[0].parent.parent

    assessments = {}
    for tr in table('tr')[1:-1]:
      title = tr.contents[1].text.strip()
      href = tr.a['href'] # eg: href="editassessment.asp?id=441406"
      # match the number
      i = re.match(r"[^\d]*(\d+)", href).group(1)
      assessments[title] = i

    return assessments

  def chooseAssessment(self):
    assessments = self.getAssessments()
    keys = sorted(assessments.keys())
    for i, ass in enumerate(keys):
      print colored(i, 'green') + ' %s (%s)' % (ass, assessments[ass])

    i = int(raw_input(colored('choice ? ', 'green')))
    
    return assessments[keys[i]]