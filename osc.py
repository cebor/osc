#!/usr/bin/env python

from pyquery import PyQuery as pq
from urlparse import parse_qs
import requests
import ConfigParser
import os.path

if os.path.isfile('config.ini'):
  config = ConfigParser.ConfigParser()
  config.read('config.ini')

  auth = {
    'asdf': config.get('CREDENTIALS', 'user'),
    'fdsa': config.get('CREDENTIALS', 'pwd'),
    'submit': 'Anmelden'
  }

  ids = {
    'kontoOnTop': config.get('IDS', 'kontoOnTop'),
    'konto': config.get('IDS', 'konto')
  }

  startId = int(config.get('BRUTFORCE', 'startId'))
  rng = int(config.get('BRUTFORCE', 'range'))

  url = 'https://qis.fh-rosenheim.de/qisserver/'
  auth_url = url + 'rds?state=user&type=1&category=auth.login'
  link_url = url + 'rds?state=change&type=1&moduleParameter=studyPOSMenu&next=menu.vm&xml=menu'
  content_url = url + 'rds?state=notenspiegelStudent&next=list.vm&nextdir=qispos/notenspiegel/student' + \
      '&createInfos=Y&struct=abschluss&nodeID=auswahlBaum|abschluss:abschl=84,stgnr=1,stg=INF,pversion=20122' + \
      '|studiengang:stg=INF|kontoOnTop:labnrzu=%(kontoOnTop)s|konto:labnrzu=%(konto)s' % (ids)

s = requests.session()

def asi():
  s.post(auth_url, data=auth)
  r = s.get(link_url)
  doc = pq(r.text)
  asi, = parse_qs(doc('a[href*=asi]').attr('href'))['asi']
  return asi


def brutforce(startId, rng, asi):
  for i in range(int(rng)):
    idn = startId
    idn = idn + i
    param = '|pruefung:labnr=%s' % (idn)

    r = s.get(content_url + param + '&asi=' + asi)
    doc = pq(r.text)

    subject = doc('table tr td.tabelle1:nth-child(2)').text()
    score = doc('table tr td.tabelle1:nth-child(4)').text()

    if subject and score:
      print(subject + ' - ' + score)


def config():
  if not os.path.isfile('config.ini'):
    config = ConfigParser.ConfigParser()
    config.add_section('CREDENTIALS')
    config.add_section('IDS')
    config.add_section('BRUTFORCE')
    config.set('CREDENTIALS', 'user', 'username')
    config.set('CREDENTIALS', 'pwd', 'passsword')
    config.set('IDS', 'kontoOnTop', '')
    config.set('IDS', 'konto', '')
    config.set('BRUTFORCE', 'startId', '1873537')
    config.set('BRUTFORCE', 'range', '1000')
    with open('config.ini', 'w') as configfile:
      config.write(configfile)
    print('Creating config.ini! Please setup and rerun!')
    return False
  return True


if __name__ == "__main__":
  if config():
    brutforce(startId, rng, asi())
