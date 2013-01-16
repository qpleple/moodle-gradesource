# -*- coding: utf-8 -*-

import requests, re, sys, csv
from BeautifulSoup import BeautifulSoup
from termcolor import colored, cprint

class Moodle():
  loginUrl      = "https://csemoodle.ucsd.edu/login/index.php"
  gradesRootUrl = "https://csemoodle.ucsd.edu/grade/report/grader/"
  reportUrl     = "https://csemoodle.ucsd.edu/mod/quiz/report.php?id=%s&pagesize=300"
  exportUrl     = "https://csemoodle.ucsd.edu/grade/export/txt/export.php"
  gradesUrl = gradesRootUrl + "index.php?id=%s"
  cookies = None
  
  def __init__(self, username, passwd):
    cprint('Logging into Moodle with username %s' % username, 'yellow')
    postData = {"username" : username, "password" : passwd}
    response = requests.post(self.loginUrl, data = postData)
    self.cookies = response.cookies

    if re.search(r"Invalid login", response.text):
        print colored(' Wrong login/password ', 'white', 'on_red')
        sys.exit()
  
  def quizFeedback(self, reportId, col):
    url = self.reportUrl % reportId
    cprint('Downloading Moodle report page %s' % url, 'yellow')
    
    html = requests.get(url, cookies = self.cookies).content
    
    cprint('Parsing the HTML', 'yellow')
    soup = BeautifulSoup(html)
    
    feedback = {}
    table = soup.find("table", id="attempts")
    for tr in table('tr', {'class': re.compile("r*")}):
      try:
        name = tr.find('td', 'c2').text.strip()
        if name == 'Overall average':
          continue
      except Exception, e:
        continue
      urlFeedback = tr.find('td', 'c%s' % col).a['href']
      content = requests.get(urlFeedback, cookies = self.cookies).content
      soup2 = BeautifulSoup(content)
      comment = soup2.find('div', 'answer').input['value']
      print '%s %s' % (name, colored(comment, 'green'))
      feedback[name] = comment
      
      
    return feedback

  def getAllScores(self, courseId):
    """
      Call the export functionnality and returns (header, scores) with:
      header = ['First Name', 'Surname', ...]
      scores [['Quentin', 'Pleple', ...], ...]
      Fields: 0:FN, 1:LN, 2:id, 3:inst, 4:dpt, 5:email, 6:total, >6:all scores
    """
    url = self.exportUrl
    payload = {'id': courseId, 'itemids': '', 'separator': 'tab'}

    txt = requests.get(url, params = payload, cookies = self.cookies).content
    data = [row for row in csv.reader(txt.splitlines(), delimiter = '\t')]
    return data[0], data[1:]

  def getScores(self, courseId):
    """Like getAllScores() but for only one assignement"""

    header, scores = self.getAllScores(courseId)
    for i, title in enumerate(header[7:]):
      print colored(i, 'green') + ' ' + title

    i = int(raw_input(colored('choice ? ', 'green')))

    header = [x for j, x in enumerate(header) if j <= 6 or j - 7 == i]
    scores = [[x for j, x in enumerate(row) if j <= 6 or j - 7 == i] for row in scores]

    return header, scores