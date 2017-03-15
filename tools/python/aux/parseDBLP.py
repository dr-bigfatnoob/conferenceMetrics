import os, sys, time

from pip._vendor.requests.packages.urllib3 import response

sys.path.append('..')
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup as Soup
import urllib2
import requests
from unicodeMagic import UnicodeReader, UnicodeWriter

dataPath = os.path.abspath("../../../data")

xmlpath = os.path.join(dataPath, 'web', 'msr', 'msr2013.xml')

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
RE_BASE_URI = "http://dblp.uni-trier.de/rec/xml/conf/re/"
ISSTA_BASE_URI = "http://dblp.uni-trier.de/rec/xml/conf/issta/"
ICST_BASE_URI = "http://dblp.uni-trier.de/rec/xml/conf/icst/"
ESEM_BASE_URI = "http://dblp.uni-trier.de/rec/xml/conf/esem/"


def parse_saner():
  f = open(os.path.join(dataPath, 'web2csv', 'conferences', 'saner.csv'), "wb")
  writer = UnicodeWriter(f)
  conf_path = os.path.join(dataPath, 'web', 'conferences', 'saner')
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


def parse_dblp_old(name, paper_type):
  f = open(os.path.join(dataPath, 'web2csv', paper_type, '%s.csv'%name), "wb")
  writer = UnicodeWriter(f)
  conf_path = os.path.join(dataPath, 'web', paper_type, name)
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
          # year, authors, title, pages, pageCount = format_dblp_xml(base_uri + item.attrib["id"] + ".xml")
          year, authors, title, pages, page_count = format_dblp_xml(get_link_uri(item))
        except urllib2.HTTPError, e:
          if e.code == 429:
            print "SLEEPING FOR 1 min"
            time.sleep(60)
            year, authors, title, pages, page_count = format_dblp_xml(get_link_uri(item))
            # year, authors, title, pages, page_count = format_dblp_xml(base_uri + item.attrib["id"] + ".xml")
          else:
            raise
        writer.writerow([year, authors, title, pages, page_count, topic, ""])
  f.close()


JOURNAL_BASE_URI='http://dblp.uni-trier.de/db/journals'
JOURNAL_XML_BASE_URI = 'http://dblp.uni-trier.de/rec/xml'

def parse_dblp_new(name, volumes, paper_type, base_uri=JOURNAL_BASE_URI):
  f = open(os.path.join(dataPath, 'web2csv', paper_type, '%s.csv' % name), "wb")
  writer = UnicodeWriter(f)
  for volume in volumes:
    uri = "%s/%s/%s%d.html" % (base_uri, name, name, volume)
    print(uri)
    resp = requests.get(uri)
    if resp.status_code != 200:
      print(resp.headers)
      print("Status code: %d for %s%d.\nVerify URI: %s" % (resp.status_code, name, volume, uri))
      return
    soup = Soup(resp.content, "html").html
    current = soup.find("body").find("h2").parent
    topic = get_text(current)
    while True:
      current = current.find_next_sibling()
      if current.name == "ul":
        for li in current.find_all("li", recursive=False):
          xml_uri = "%s/%s.xml" % (JOURNAL_XML_BASE_URI, li.attrs['id'])
          try:
            year, authors, title, pages, page_count = format_dblp_xml(xml_uri)
          except urllib2.HTTPError, e:
            if e.code == 429:
              print "SLEEPING FOR 1 min"
              time.sleep(60)
              year, authors, title, pages, page_count = format_dblp_xml(xml_uri)
            else:
              raise
          writer.writerow([year, authors, title, pages, page_count, topic, ""])
      elif current.name == "header":
        topic = get_text(current)
      if current.name == "div":break


def get_text(bs_elem):
  return bs_elem.text.replace("\n", "")


def format_dblp_xml(xml_uri):
  print xml_uri
  tree = ET.ElementTree(file=urllib2.urlopen(xml_uri))
  root = tree.getroot()
  year = root[0].findall("year")[0].text
  title = root[0].findall("title")[0].text
  if title is None:
    title = ''.join(root[0].findall("title")[0].itertext())
  authors = ",".join([author.text for author in root[0].findall("author")])
  pages = root[0].findall("pages")
  if pages:
    pages = pages[0].text
    splits = pages.strip().split("-")
    try:
      if len(splits) > 1 and splits[1] and splits[0]:
        page_count = str(int(splits[1].split(":")[-1]) - int(splits[0].split(":")[-1]) + 1)
      else:
        page_count = "1"
    except ValueError:
      page_count = "1"

  else:
    pages, page_count = "", ""
  return year, authors, title, pages, page_count


def get_link_uri(item):
  a = [element for element in item.getiterator() if element.text == 'XML']
  if len(a) > 0:
    return a[0].attrib["href"]
  return None

def _main():
  journal = "sigsoft"
  start = 24
  end = 32
  parse_dblp_new(journal, range(end,start-1,-1), "journals")
  # parse_dblp_old('esem', 'conferences')
  # parse_saner()


if __name__ == "__main__":
  _main()
