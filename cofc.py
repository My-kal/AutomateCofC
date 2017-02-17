"""
CofC.py
author: Mykal | <devmykal@protonmail.com>
created: 14-Nov-2016
updated: 21-Dec-2016
version: 1
"""

from apscheduler.schedulers.blocking import BlockingScheduler
from bs4 import BeautifulSoup as bs
import json
from random import randint
import requests
import time
import smtplib
import sys


config = json.loads(open('userinfo.json').read())
sub = config['subject'].strip()
course_num = config['course_num'].strip()
crn_list = config['crns'].split(',')
term = config['term'].strip()


def main():
    def sleep():
        wait_interval = (randint(10, 60))
        time.sleep(wait_interval)
        
    base_url = 'https://ssb.cofc.edu:9710'
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) '
        'AppleWebKit/601.6.17 (KHTML, like Gecko) Version/9.1.1 Safari/601.6.17',
        'Referer': 'https://www.google.com/',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    })
    
    # main page
    url = base_url + '/prod/bwckschd.p_disp_dyn_sched'
    r = session.get(url)
    sleep()
    
    # get term
    p_term = ''
    soup = bs(r.text, 'html.parser')
    for s in soup.find('select', {'id':'term_input_id'}).find_all('option'):
        if term in s.string:
            if 'View only' not in s.string:
                p_term = s['value']
                break
    
    if not p_term:
        sys.exit(term + ' is not available')
         
    # choose term
    url = base_url + '/prod/bwckgens.p_proc_term_date'
    payload = {
        'p_calling_proc': 'bwckschd.p_disp_dyn_sched',
        'p_term': p_term
        }
    session.post(url, data=payload)
    sleep()
    
    # choose course
    url = base_url + '/prod/bwckschd.p_get_crse_unsec'
    payload = {
        'begin_ap': 'a',
        'begin_hh': '0',
        'begin_mi': '0',
        'end_ap': 'a',
        'end_hh': '0',
        'end_mi': '0',
        'sel_attr': ['dummy', '%'],
        'sel_camp': ['dummy', '%'],
        'sel_crse': course_num,
        'sel_day': 'dummy',
        'sel_insm': 'dummy',
        'sel_instr': 'dummy',
        'sel_levl': ['dummy', '%'],
        'sel_ptrm': ['dummy', '%'],
        'sel_schd': ['dummy', '%'],
        'sel_sess': ['dummy', '%'],
        'sel_subj': ['dummy', sub],
        'sel_title': '',
        'term_in': p_term
    }
    r = session.post(url, data=payload)
    sleep()
    
    # find crn
    soup = bs(r.text, 'html.parser')
    try:
        openings = ['***** Open Courses *****']
        course_urls = []
    
        table = soup.find('table', {'class': 'datadisplaytable'})
    except AttributeError as e:
        raise ValueError('Table not found', e)
    
    for url in table.find_all('th', {'class': 'ddtitle'}):
        url = url.find('a')['href']
        course_urls.append(base_url + url)

    # iterate through each course, find openings
    for course in course_urls:
        r = session.get(course)
        soup = bs(r.text, 'html.parser')
        rem = soup.find_all('td', {'class': 'dddefault'})[3].string  # remaining open seats
    
        if rem > '0':
            text = soup.find('th', {'class': 'ddlabel'}).text
            if crn_list:
                if any(crn.strip() in text for crn in crn_list):  # any crn in text
                    openings.append(text)
            else:  # crn list is empty
                openings.append(text)
    
    # notify via email
    if len(openings) > 1:
        msg = '\n'.join(openings)
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(config['sending']['email'], config['sending']['password'],)
            server.sendmail(config['receiving']['email'], config['receiving']['password'], msg)
        except smtplib.SMTPException as e:
            print(e)
            
scheduler = BlockingScheduler()
scheduler.add_job(main, 'interval', minutes=25)
scheduler.start()
