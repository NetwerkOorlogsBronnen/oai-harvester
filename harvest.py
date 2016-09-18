#!/usr/bin/env python
# Harvester based on the OAI harvester (simple version called harvest.py) of Q42 to harvest the Rijksmuseum collection.
# changes are made to implement right base url and deal with different type of ResumptionToken
# Netwerk Oorlogsbronnen does not work with an apikey so lines dealing with an api key are commented

import urllib2, os, sys
from xml.dom import minidom

base_url = raw_input("Enter base_url for oai source: ")
if len(base_url) < 2: 
  base_url = 'http://oaicat.oorlogsbronnen.knaw.nl/OAIHandler'

#after initially allowing multiple metdata Prefixes I noticed that all records can be exported as ese or oai_dc. ESE contains more data so I made ESE the default metadata Prefix.
meta_prefix = raw_input("Enter metadata prefix for oai source: ")
if len(meta_prefix) < 2: 
  meta_prefix = 'ese'
  
url = base_url + '?verb=ListRecords&metadataPrefix=' + meta_prefix 

# oorlogsbronnen and Beeldbank WO2 cannot harvest files with a resumption token and a metadataprefix. That is why I had to make this extra condition to
# exclude metadata prefix from url2 for oorlogsbronnen.
if (base_url == 'http://oaicat.oorlogsbronnen.knaw.nl/OAIHandler') or (base_url == 'http://www.beeldbankwo2.nl/wo2-no-webservice/oai-pmh'):
  url2 = base_url + '?verb=ListRecords&resumptionToken='
else:
  url2 = base_url + '?verb=ListRecords&metadataPrefix=' + meta_prefix + '&resumptionToken='

set_name = raw_input("Enter set name for oai source: ")
if len(set_name) > 2: 
	url = url + '&set=' + set_name
else:
	set_name = meta_prefix
	

count = 0 # keep track of number of records harvested
token = ''

def getText(nodelist):
  rc = []
  for node in nodelist:
      if node.nodeType == node.TEXT_NODE:
          rc.append(node.data)
  return ''.join(rc)

def harvest(url):
  print "downloading: " + url
  data = urllib2.urlopen(url)

  # cache the data because this file-like object is not seekable
  cached  = ""
  for s in data:
    cached += s

  dom = minidom.parseString(cached)

  # check for error
  error = dom.getElementsByTagName('error')
  if len(error) > 0:
    errType = error[0].getAttribute('code')
    desc = getText(error[0].childNodes)
    raise Exception(errType + ": " +desc)

  save(cached)

  countRecords = len(dom.getElementsByTagName('record'))

  nodelist = dom.getElementsByTagName('resumptionToken')
  if len(nodelist) == 0: return None, countRecords
  strToken = getText(nodelist[0].childNodes)

  return strToken, countRecords

def save(data):
  # first establish f there is a path to a directory to store the files in.
  mypath = set_name
  if not os.path.isdir(mypath):
    os.makedirs(mypath)
  
  filename = set_name + str(count) + '.xml'
  
  print 'saving: ' + filename
  with open(mypath + '/' + filename, 'w') as f:
    for s in data:
      f.write(s)

try:
  token, countRecords = harvest(url)
  count += countRecords

  while token:
    token, countRecords = harvest(url2 + token)
    count += countRecords
    print count

except:
  print "\n!!!"
  print "Unexpected error"
  print "!!!\n"
  raise