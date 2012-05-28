#!/usr/bin/env python

from dumptruck import DumpTruck

dt=DumpTruck(dbname='avloppsguiden.sqlite')
dt.execute('''
create table if not exists page_sources (
  url text not null,
  unique(url),
  source text not null
);''')

dt.execute('''
create table if not exists todo (
  url text not null,
  unique(url) on conflict ignore
);''')


