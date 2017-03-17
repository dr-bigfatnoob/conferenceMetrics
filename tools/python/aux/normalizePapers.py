# This Python file uses the following encoding: utf-8

import os
import sys
sys.path.append('..')
# from folderUtils import MyFolder
from dictUtils import MyDict
from unicodeMagic import UnicodeReader, UnicodeWriter
from unidecode import unidecode
from nameMagic import normaliseName, directLookup, reverseLookup


dataPath = os.path.abspath("../../../data")


CONFERENCES = ['icse', 'icsm', 'wcre', 'csmr', 'msr', 'gpce', 'fase', 'icpc', 'fse',
               'scam', 'ase', 'saner', 'ssbse', 're', 'issta', 'icst', 'esem']
JOURNALS = ["jss", "tse", "software", "ese", "spe", "ijseke", "isse", "smr", "sigsoft",
            "rej", "tosem", "asej", "sqj", "stvr"]


def normalize_file(reader, writer):
  for row in reader:
    year = row[0]
    authors = []
    for name in row[1].split(','):
      cleanName = normaliseName(name)
      if len(cleanName):
        authors.append(cleanName)
    authors = ','.join(authors)
    writer.writerow([year, authors] + row[2:])


def normalize_conferences():
  for conference in CONFERENCES:
    print conference
    f = open(os.path.join(dataPath, 'bht2csv', '%s_papers.csv' % conference), 'rb')
    reader = UnicodeReader(f)
    g = open(os.path.join(dataPath, 'normalised-papers', 'conferences', '%s.csv' % conference), 'wb')
    writer = UnicodeWriter(g)
    normalize_file(reader, writer)
    f.close()
    g.close()


def normalize_journals():
  for journal in JOURNALS:
    print journal
    f = open(os.path.join(dataPath, 'web2csv', 'journals', '%s.csv' % journal), 'rb')
    reader = UnicodeReader(f)
    g = open(os.path.join(dataPath, 'normalised-papers', 'journals', '%s.csv' % journal), 'wb')
    writer = UnicodeWriter(g)
    normalize_file(reader, writer)
    f.close()
    g.close()

normalize_journals()
# normalize_conferences()