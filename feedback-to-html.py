from cPickle import *
f = load(open('feedback.pickle'))


with open('feedback.html', 'wb') as html:
  for name, data in f.items():
    html.write("<b>%s</b> %s" % (name, data['feedback']))
    html.write("<br>\n")