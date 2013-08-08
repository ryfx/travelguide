# -*- coding: utf-8 -*-
import sys
import os
import urllib
import shutil
from bs4 import BeautifulSoup

reload(sys)
sys.setdefaultencoding('utf-8')

def cleanUp(soup):
  content = soup.find("div", {"id": "content"})

  # remove all specified tags
  [s.decompose() for s in content(['noscript'])]

  [s.decompose() for s in content.findAll("a", {"id": "mw-mf-last-modified"})]
  [s.decompose() for s in content.findAll("span", {"class": "mw-editsection"})]
  [s.decompose() for s in content.findAll("table", {"class": "articleState"})]
  [s.decompose() for s in content.findAll("button", {"class": "languageSelector"})]
  [s.decompose() for s in content.findAll("a", {"class": "section_anchors"})]
  [s.decompose() for s in content.findAll("div", {"id": "mw-mf-language-section"})]

  # delete empty sections
  sections = content.findAll("div", {"class": "section"})
  for section in sections:
    hasText = 0
    for string in section.div.stripped_strings:
      hasText += 1
    if not hasText:
      section.decompose()

  # Wrap content with our own header and body, and restore original div structure for css
  divContentWrapper = soup.new_tag("div", id="content_wrapper")
  divContentWrapper["class"] = "show"
  content = content.wrap(divContentWrapper)
  content = content.wrap(soup.new_tag("div", id="mw-mf-page-center"))
  content = content.wrap(soup.new_tag("div", id="mw-mf-viewport"))
  bodyTag = soup.new_tag("body")
  bodyTag["class"] = "mediawiki ltr sitedir-ltr mobile stable skin-mobile action-view"
  content = content.wrap(bodyTag)
  htmlTag = soup.new_tag("html", lang="en", dir="ltr")
  htmlTag["class"] = "client-js"
  content = content.wrap(htmlTag)
  # Here we add our own js and css into the <head>
  headTag = soup.new_tag("head")
  headTag.append(soup.new_tag("meta", charset="UTF-8"))
  headTag.append(soup.new_tag("link", rel="stylesheet", type="text/css", href="css/article.css"))
  headTag.append(soup.new_tag("script", type="text/javascript", src="js/article.js"))
  meta1 = soup.new_tag("meta", content="yes")
  # workaround as "name" is used in python
  meta1["name"] = "apple-mobile-web-app-capable"
  headTag.append(meta1)
  meta2 = soup.new_tag("meta", content="initial-scale=1.0, user-scalable=yes, minimum-scale=0.25, maximum-scale=1.6")
  meta2["name"] = "viewport"
  headTag.append(meta2)
  content.body.insert_before(headTag)

  return content

if __name__ == '__main__':
  if len(sys.argv) < 2:
    print "Usage: " + sys.argv[0] + " <inFile> [outFile]"
    exit(1)

  file = sys.argv[1]
  soup = BeautifulSoup(open(file))
  soup = cleanUp(soup)
  file = sys.stdout
  if len(sys.argv) > 2:
    file = open(sys.argv[2], 'w')
  file.write(soup.encode('utf-8'))