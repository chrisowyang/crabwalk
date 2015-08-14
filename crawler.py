#page element scraper

"""
This program is designed to 
	1.) scrape a list of URLs for title tags, meta description, and body text
	2.) scan each element for fuzzy keyword matches based on inputted keywords
	3.) output a csv with elements and their respective counts 

inputs: URLs and respective keywords
outputs: text and counts

Requires (installed via pip or other package manager):
	BeautifulSoup (scraping package)
	FuzzyWuzzy (fuzzy matching package)
	NLTK (natural language processor)

Should be standard with Python 3:
	requests
	csv
	os

Extensions:
	textstat readability analysis 
"""

from bs4 import BeautifulSoup
import requests
import csv
from fuzzywuzzy import fuzz
import nltk.data
from nltk.tokenize import RegexpTokenizer
#from textstat.textstat import textstat
import time
import re
import os
import base64
import httplib2


def scrape(URL,KW):
	headers = {'User-Agent' : "Mozilla/5.0 (Windows NT 6.0; WOW64) AppleWebKit/534.24 (KHTML, like Gecko) Chrome/11.0.696.16 Safari/534.24"}

	start = time.time()
	#for URL in URLlist:
	end = URL[-10:]
	if "pdf" in end.lower():
		return ["NA","NA",[0,1,2],"NA","NA","NA","NA","NA","NA","NA"]
	else:
		r = requests.get(URL,headers=headers,timeout=25)
		stripped = r.text
		stripped = stripped.replace('\n', '. ')
		soup = BeautifulSoup(stripped,"html.parser")
		
	load_time = start - time.time()
	#TITLE TAGS
	start = time.time()
	try:
		title = soup.title.string
		title = title.replace(".   ","")
		title = title.replace(".  ","")
		if title == None:
			title = u"NA"
	except:
		title = u"NA"
	
	#META DESCRIPTION
	try:
		md = soup.findAll(attrs={"name":"description"})
		if md != []:
			meta_raw = md
		else: 
			meta_raw = soup.findAll(attrs={"name":"Description"})
		meta = meta_raw[0]['content']
	except:
		meta = u"NA"

	#H1
	try:
		H1 = soup.h1.string
		H1 = H1.replace(".   ","")
		H1 = H1.replace(".  ","")
		if H1 == None:
			H1 = u"NA"
	except:
		H1 = u"NA"

	#links
	bareresult = url_cleaner(URL)
	links_list = []
	exlinks = 0
	inlinks = 0
	exlinks_cc = 0
	inlinks_cc = 0

	for link in soup.find_all(href=re.compile("https?://")):
		full_link=link.get('href')
		clean_link = url_cleaner(link.get('href'))
		if clean_link == bareresult:
			links_list.append(clean_link)
			exlinks += 1
			exlinks_cc += len(full_link)
		else:
			inlinks += 1
			inlinks_cc+= len(full_link)


	#BODY
	
	try:
		
		end = URL[-10:]
		if "pdf" in end.lower():
			text = "PDF"
		else:
			for script in soup(["script", "style"]):
				script.extract()
			text = soup.get_text()
			text = text.replace(',',' ')
			text = text.replace('<br/>','. ')
			text = text.replace('\r',' ')
			text = text.replace('\t', ' ')
			text = text.replace('.   ', '')
			text = text.replace('.  ', '')
			text = text.replace('. . ', '')
			starting = text[0:10]
			if "pdf" in starting.lower():
				text = "PDF"
		text_count = count(text, KW)

	except:	
		text = u"NA"
	parse_time = time.time() -start

	content = [title, meta, text_count, H1, exlinks, inlinks, exlinks_cc, inlinks_cc,load_time, links_list] 
	return content

def count(text):
	text = text.lower()
	
	sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
	sentences = sent_detector.tokenize(text.strip())

	tokenizer = RegexpTokenizer(r'\w+')
	wordcount = 0

	for sentence in sentences:
		tokens = tokenizer.tokenize(sentence)
		words = len(tokens)
		wordcount += words
	
	text = text.replace('   ', '')
	text = text.replace('.', ' ')
	text = text.replace('   ', '')
	character_count = len(text)

	return [wordcount,character_count]



def analysis(basecsv,output):
	rows = []
	queue = []
	with open(output,'wt') as myfile:
		wr = csv.writer(myfile)
		wr.writerow(['URL','position', 'load time', 'title tag text', 'meta tag text', 'h1 text','title tag count', 'meta description count','h1 count', 'body count','body word count','body character count','ex links','in links','ex links cc','in links cc'])
		with open(basecsv,'rU', encoding='Latin-1') as fp:
			reader = csv.reader(fp,delimiter=",")
			

			for row in reader:
				rows.append(row)

			URL = rows[0]
			black = [x for x in rows[1]]
			white = [x for x in rows[2]]
			queue.append(URL)


		while len(queue)>0:
			if white == [] or :
			if black in queue[0]:
				try:
					content = scrape(queue[0])
				except:
					content = ["NA","NA",[0,1,2],"NA","NA","NA","NA","NA","NA","NA"]


				titletag = content[0]
				meta = content[1]
				H1 = content[3]

				titletag_count = count(titletag, KW)
				meta_count = count(meta, KW)
				body_count = content[2]
				H1_count = count(H1, KW)


				wr.writerow([KW,URL, position, content[8], titletag, meta, H1, titletag_count[0], meta_count[0],H1_count[0],body_count[0],body_count[1],body_count[2],content[4],content[5],content[6],content[7]])


def url_cleaner(url):
	"""
	this function matches and cleans a given url to aid in easier matching and dictionary construction later on
	"""
	url_match = re.match("(https?://)?(.*?)\.(.*?)/",url)
	if url_match != None:
		if '.' not in url_match.group(3):
			return url_match.group(2)+'.' +url_match.group(3)
		else:
			return url_match.group(3)



if __name__ == '__main__':
	activate()

