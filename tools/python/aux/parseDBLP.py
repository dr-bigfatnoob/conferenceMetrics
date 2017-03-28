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
          year, authors, title, pages, page_count, doi = format_dblp_xml(get_link_uri(item))
        except urllib2.HTTPError, e:
          if e.code == 429:
            print "SLEEPING FOR 1 min"
            time.sleep(60)
            year, authors, title, pages, page_count, doi = format_dblp_xml(get_link_uri(item))
            # year, authors, title, pages, page_count = format_dblp_xml(base_uri + item.attrib["id"] + ".xml")
          else:
            raise
        writer.writerow([year, authors, title, doi, pages, page_count, topic, ""])
  f.close()


JOURNAL_BASE_URI='http://dblp.uni-trier.de/db/journals'
JOURNAL_XML_BASE_URI = 'http://dblp.uni-trier.de/rec/xml'

def parse_dblp_new(name, volumes, paper_type, base_uri=JOURNAL_BASE_URI, f_name=None):
  if f_name is None:
    f_name = name
  f = open(os.path.join(dataPath, 'web2csv', paper_type, '%s.csv' % f_name), "wb")
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
            year, authors, title, pages, page_count, doi = format_dblp_xml(xml_uri)
          except urllib2.HTTPError, e:
            if e.code == 429:
              print "SLEEPING FOR 1 min"
              time.sleep(60)
              year, authors, title, pages, page_count, doi = format_dblp_xml(xml_uri)
            else:
              raise
          writer.writerow([year, authors, title, doi, pages, page_count, topic, ""])
      elif current.name == "header":
        topic = get_text(current)
      if current.name == "div":break


def get_text(bs_elem):
  return bs_elem.text.replace("\n", "")


def format_dblp_xml(xml_uri):
  print xml_uri
  try:
    tree = ET.ElementTree(file=urllib2.urlopen(xml_uri))
  except:
    print "SLEEPING FOR 1 min"
    time.sleep(60)
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
  doi = root[0].findall("ee")
  if doi:
    doi = doi[0].text
  else:
    doi = ""
  return year, authors, title, pages, page_count, doi


def get_link_uri(item):
  a = [element for element in item.getiterator() if element.text == 'XML']
  if len(a) > 0:
    return a[0].attrib["href"]
  return None

def _parse_journal():
  journal = "stvr"
  ref = None
  start = 1
  end = 26
  parse_dblp_new(journal, range(end, start - 1, -1), "journals", f_name=ref)

def _main():
  _parse_journal()
  # parse_dblp_old('wcre', 'conferences')


if __name__ == "__main__":
  _main()
