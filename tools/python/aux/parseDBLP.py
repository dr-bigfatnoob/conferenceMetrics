import os, sys, time
sys.path.append('..')
import xml.etree.ElementTree as ET
import urllib2
from unicodeMagic import UnicodeReader, UnicodeWriter

dataPath = os.path.abspath("../../../data")

xmlpath = os.path.join(dataPath, 'web', 'msr', 'msr2013.xml')
print xmlpath

ASE_BASE_URI = "http://dblp.uni-trier.de/rec/xml/conf/kbse/"
MSR_BASE_URI = "http://dblp.uni-trier.de/rec/xml/conf/msr/"
CSMR_BASE_URI = "http://dblp.uni-trier.de/rec/xml/conf/csmr/"
WCRE_BASE_URI = "http://dblp.uni-trier.de/rec/xml/conf/wcre/"
FASE_BASE_URI = "http://dblp.uni-trier.de/rec/xml/conf/fase/"
FSE_BASE_URI = "http://dblp.uni-trier.de/rec/xml/conf/sigsoft/"
GPCE_BASE_URI = "http://dblp.uni-trier.de/rec/xml/conf/gpce/"
ICPC_BASE_URI = "http://dblp.uni-trier.de/rec/xml/conf/iwpc/"
ICSE_BASE_URI = "http://dblp.uni-trier.de/rec/xml/conf/icse/"
ICSM_BASE_URI = "http://dblp.uni-trier.de/rec/xml/conf/icsm/"
SCAM_BASE_URI = "http://dblp.uni-trier.de/rec/xml/conf/scam/"
SSBSE_BASE_URI = "http://dblp.uni-trier.de/rec/xml/conf/ssbse/"

def parse_saner():
  f = open(os.path.join(dataPath, 'web2csv', 'saner.csv'), "wb")
  writer = UnicodeWriter(f)
  conf_path = os.path.join(dataPath, 'web', "saner")
  for file_name in reversed(os.listdir(conf_path)):
    year = file_name.split("_")[1].split(".")[0]
    if int(year) < 2015:
      base_uri = CSMR_BASE_URI
    else:
      base_uri = WCRE_BASE_URI
    file_path = os.path.join(conf_path, file_name)
    print "**** %s ****" % file_path
    tree = ET.parse(file_path)
    root = tree.getroot()
    headers = root.findall('h2')
    lists = root.findall('ul')
    assert len(headers) == len(lists)
    for header, lst in zip(headers, lists):
      topic = header.text.replace("\n", "")
      for item in lst.findall("li"):
        try:
          year, authors, title, pages, pageCount = format_dblp_xml(base_uri + item.attrib["id"] + ".xml")
        except urllib2.HTTPError, e:
          if e.code == 429:
            print "SLEEPING FOR 1 min"
            time.sleep(60)
            year, authors, title, pages, pageCount = format_dblp_xml(base_uri + item.attrib["id"] + ".xml")
          else:
            raise
        writer.writerow([year, authors, title, pages, pageCount, topic, ""])
  f.close()

def parse_dblp_old(base_uri, conf):
  f = open(os.path.join(dataPath, 'web2csv', '%s.csv'%conf), "wb")
  writer = UnicodeWriter(f)
  conf_path = os.path.join(dataPath, 'web', conf)
  for file_name in reversed(os.listdir(conf_path)):
    file_path = os.path.join(conf_path, file_name)
    print "**** %s ****" % file_path
    tree = ET.parse(file_path)
    root = tree.getroot()
    headers = root.findall('h2')
    lists = root.findall('ul')
    assert len(headers) == len(lists)
    for header, lst in zip(headers, lists):
      topic = header.text.replace("\n", "")
      for item in lst.findall("li"):
        try:
          year, authors, title, pages, pageCount = format_dblp_xml(base_uri + item.attrib["id"] + ".xml")
        except urllib2.HTTPError, e:
          if e.code == 429:
            print "SLEEPING FOR 1 min"
            time.sleep(60)
            year, authors, title, pages, pageCount = format_dblp_xml(base_uri + item.attrib["id"] + ".xml")
          else:
            raise
        writer.writerow([year, authors, title, pages, pageCount, topic, ""])
  f.close()


def format_dblp_xml(xml_uri):
  print xml_uri
  tree = ET.ElementTree(file=urllib2.urlopen(xml_uri))
  root = tree.getroot()
  year = root[0].findall("year")[0].text
  title = root[0].findall("title")[0].text
  authors = ",".join([author.text for author in root[0].findall("author")])
  pages = root[0].findall("pages")[0].text
  if pages:
    splits = pages.strip().split("-")
    if len(splits) > 1:
      pageCount = str(int(splits[1]) - int(splits[0]) + 1)
    else:
      pageCount = "1"
  else:
    pages, pageCount = "", ""
  return year, authors, title, pages, pageCount




parse_dblp_old(SSBSE_BASE_URI, 'ssbse')
# parse_saner()