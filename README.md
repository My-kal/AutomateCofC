# Automate CofC
AutomateCofC will email/text you  when there are openings in courses.

### Dependencies
Python 3.5

Gmail account: Less secure apps must be enabled [https://www.google.com/settings/security/lesssecureapps]

ApScheduler

BeautifulSoup4

Requests 
```sh
$ pip install apscheduler
$ pip install bs4
$ pip install requests
```

### Installation
1. Clone the repo
2. Edit `userinfo.json`
3. Configure gmail account

The script checks every 5 minutes. To change, 
edit: `scheduler.add_job(main, 'interval', minutes=5)`

##License
AutomateCofC is licensed under the MIT license.
