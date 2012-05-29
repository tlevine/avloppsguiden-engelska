#!/usr/bin/env python2
from requests import get
from dumptruck import DumpTruck
from lxml.html import fromstring
from random import normalvariate
from time import sleep
import os

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
create table if not exists nontext_pages (
  url text not null,
  filename text not null,
  unique(url) on conflict ignore
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
        # Is it plain text?
        page_source = get(url).text

    except TypeError:
        # I guess not
        filename = url.replace('/', '_')
        path = os.path.join('.', 'binary_files', filename)
        os.system("wget -O '%s' '%s'" % (path, url))

        # Save the reference
        dt.insert({'url': url, 'filename': filename}, 'nontext_pages')

    else:
        # Save the page
        dt.insert({'url': url, 'page_source': page_source}, 'page_sources')

        # Assume it's HTML and look for more pages
        html = fromstring(page_source)
        html.make_links_absolute(url)
        todo = [{'url': unicode(url_to_visit)} for url_to_visit in html.xpath('//a/@href')]
        if len(todo) > 0:
            dt.insert(todo, 'todo')
        dt.execute('delete from todo where url not like "%avloppsguiden%"')
        dt.execute('''
delete from todo where url in (
  select url from page_sources union select url from nontext_pages
)''')

    dt.execute('delete from todo where url = ?', [url])
    dt.commit()
    randomsleep()
