from termcolor import colored, cprint

while True:
  s = 0
  for i in range(1, 8):
    n = raw_input('#%s : ' % i)
    if n != '':
      s += int(n)
  cprint(s, 'green')
  