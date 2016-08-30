import os, sys, time, csv
sys.path.append('..')
import xml.etree.ElementTree as ET
import urllib2
from unicodeMagic import UnicodeReader, UnicodeWriter

dataPath = os.path.abspath("../../../data")

def parse_csv(conf):
  f = open(os.path.join(dataPath, 'web2csv', '%s_pc.csv'%conf), "wb")
  writer = UnicodeWriter(f)
  folder_path = os.path.join(dataPath, 'web_pc', conf)
  for file_name in reversed(os.listdir(folder_path)):
    file_path = os.path.join(folder_path, file_name)
    print "**** %s ****" % file_path
    year = file_name.split("_")[1].split(".")[0]
    with open(file_path, 'r') as csvfile:
      reader = UnicodeReader(csvfile)
      for row in reader:
        writer.writerow([year, "main", row[0].strip()] + [cell.strip() for cell in row[1].strip().split(",")])
  f.close()

def parse_ase_csv():
  f = open(os.path.join(dataPath, 'web2csv', 'ase_pc.csv'), "wb")
  writer = UnicodeWriter(f)
  ase_path = os.path.join(dataPath, 'web_pc', 'ase')
  for file_name in reversed(os.listdir(ase_path)):
    file_path = os.path.join(ase_path, file_name)
    print "**** %s ****" % file_path
    year = file_name.split("_")[1].split(".")[0]
    with open(file_path, 'r') as csvfile:
      reader = UnicodeReader(csvfile)
      for row in reader:
        writer.writerow([year, "main", row[0].strip()] + [cell.strip() for cell in row[1].strip().split(",")])
  f.close()

def parse_msr():
  f = open(os.path.join(dataPath, 'web2csv', 'msr_pc.csv'), "wb")
  writer = UnicodeWriter(f)
  base_uri = "http://dblp.uni-trier.de/rec/xml/conf/msr/"
  msr_path = os.path.join(dataPath, 'web_pc', 'msr')
  for file_name in reversed(os.listdir(msr_path)):
    file_path = os.path.join(msr_path, file_name)
    print "**** %s ****" % file_path
    year = file_name.split("_")[1].split(".")[0]
    tree = ET.parse(file_path)
    if int(year) < 2016:
      parse_msr_old(tree, year, writer)
    else:
      parse_msr_new(tree, year, writer)
  f.close()

def parse_msr_new(tree, year, writer):
  root = tree.getroot()
  divs = list(root.iter("div"))
  names = []
  institutions = []
  for div in divs:
    if 'member-name' in div.attrib['class'].split(" "):
      name = div.text
      if name is None:
        name = div.findall("a")[0].text
      if name is None:
        raise RuntimeError("Check the format of name for msr in %s " % year)
      names.append(name)
    if 'member-institution' in div.attrib['class'].split(" "):
      institutions.append(div.text)
  assert len(names) == len(institutions)
  for name, institution in zip(names, institutions):
    writer.writerow([year, "main", name.strip()] + institution.strip().split(", "))


def parse_msr_old(tree, year, writer):
  root = tree.getroot()
  rows = list(root.iter("tr"))
  for row in rows:
    name = row.findall("td")[0].text
    if name is None:
      name = row.findall("td")[0].findall("a")[0].text
    if name is None:
      raise RuntimeError("Check the format of name for %s " % file_name)
    details = row.findall("td")[1].text
    writer.writerow([year, "main", name] + details.split(", "))


parse_csv("scam")