#!/usr/bin/env python2
from requests import get
from dumptruck import DumpTruck
from lxml.html import fromstring
from random import normalvariate
from time import sleep

dt = DumpTruck(dbname = 'avloppsguiden.sqlite', auto_commit = False)

# Etiquette
def randomsleep(mean = 30, sd = 10):
    seconds=normalvariate(mean,sd)
    if seconds>0:
        sleep(seconds)

# Initialize
dt.execute('''
create table if not exists page_sources (
  url text not null,
  page_source text not null,
  unique(url)
);''')

dt.execute('''
create table if not exists todo (
  url text not null,
  unique(url) on conflict ignore
);''')
dt.insert({'url': 'http://husagare.avloppsguiden.se/'}, 'todo')
dt.commit()

# Crawl
while dt.execute('select count(*) as c from todo')[0]['c'] > 0:
    url = dt.execute('select url from todo limit 1')[0]['url']
    print 'Crawling %s' % url
    try:
        page_source = get(url).text
    except TypeError:
        page_source = get(url).content
#   page_source = page_source.decode('utf-8')

    # Save that page
    dt.insert({'url': url, 'page_source': page_source}, 'page_sources')

    # Look for more pages
    html = fromstring(page_source)
    html.make_links_absolute(url)
    todo = [{'url': unicode(url_to_visit)} for url_to_visit in html.xpath('//a/@href')]
    dt.insert(todo, 'todo')

    dt.execute('delete from todo where url = ?', [url])
    dt.commit()
    randomsleep()
