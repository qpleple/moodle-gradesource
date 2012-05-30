# -*- coding: utf-8 -*-

import requests, re, sys
from BeautifulSoup import BeautifulSoup
from termcolor import colored, cprint

class Moodle():
  loginUrl      = "https://csemoodle.ucsd.edu/login/index.php"
  gradesRootUrl = "https://csemoodle.ucsd.edu/grade/report/grader/"
  reportUrl     = "https://csemoodle.ucsd.edu/mod/quiz/report.php?id=%s&pagesize=300"
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
  
  def quizGradesFromUrl(self, col, url):
    grades = {}

    cprint('Downloading Moodle grade page %s' % url, 'yellow')
    html = requests.get(url, cookies = self.cookies).content
    
    cprint('Parsing the HTML for column %s' % col, 'yellow')
    soup = BeautifulSoup(html)
    table = soup.find('table', id = "user-grades")
  
    for tr in table('tr', {'class' : re.compile('^r')}):
      name = tr.th.contents[1].string.strip()
      scoreTd = tr.find('td', {'class' : re.compile('c%s' % col)})
      scoreStr = scoreTd.span.string
      if scoreStr != "-":
        grades[name] = int(float(scoreStr))
    
    paging = soup.find('div', {'class' : 'paging'})
    otherPages = [a['href'] for a in paging('a') if re.match('\d', a.text)]
    
    return grades, otherPages
    
  def quizGrades(self, column, courseId):
    # First page
    url = self.gradesUrl % courseId
    grades, otherPages = self.quizGradesFromUrl(column, url)
    print grades.keys()
    
    # Other pages
    cprint('Other pages:', 'yellow')
    for otherPage in otherPages:
      cprint('* %s' % otherPage, 'yellow')
      
    for otherPage in otherPages:
      url = self.gradesRootUrl + otherPage
      temp, _ = self.quizGradesFromUrl(column, url)
      print temp.keys()
      grades.update(temp)
    
    return grades
  
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
