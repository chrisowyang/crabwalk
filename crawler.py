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

import nltk.data
from nltk.tokenize import RegexpTokenizer
import time
import re
import sys
#import random



def scrape(URL,baseURL):
	headers = {'User-Agent' : "Mozilla/5.0 (Windows NT 6.0; WOW64) AppleWebKit/534.24 (KHTML, like Gecko) Chrome/11.0.696.16 Safari/534.24"}
	
	start = time.time()

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

	for link in soup.find_all('a', href=True):
		full_link=link.get('href')
		clean_link = url_cleaner(link.get('href'))
		if clean_link == bareresult:
			links_list.append(clean_link)
			inlinks += 1
			inlinks_cc += len(full_link)
		elif 'http' not in full_link:

			links_list.append(baseURL+full_link)
			inlinks += 1
			inlinks_cc += len(full_link)
		else:
			exlinks += 1
			exlinks_cc+= len(full_link)


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
		text_count = count(text)

	except:	
		text = u"NA"


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
	visited = []
	with open(output,'wt') as myfile:
		wr = csv.writer(myfile)
		wr.writerow(['URL', 'load time', 'title tag text', 'meta tag text', 'h1 text','title tag count', 'meta description count','h1 count', 'body word count','body character count','ex links','in links','ex links cc','in links cc'])

		with open(basecsv,'rU', encoding='Latin-1') as fp:
			reader = csv.reader(fp,delimiter=",")
		
			for row in reader:
				rows.append(row)

			URL = rows[0][1]
			black = [x for x in rows[1][1:]]
			white = [x for x in rows[2][1:]]
			queue.append(URL)



		while len(queue)>0:
			targeturl = queue[0]

			targeturl = targeturl.replace("www.","")
			targeturl = targeturl.replace("//","/")
			targeturl = targeturl.replace("/./","/")
			targeturl = targeturl.replace("http:/","http://")
			targeturl = targeturl.replace("https:/","https://")


			if targeturl not in visited:

				visited.append(targeturl)
				white_dummy = 0
				black_dummy = 0 
				if targeturl == URL:
					white_dummy =1 
				elif white !=[''] or targeturl == URL:
					for x in white:
						if x != '':

							if x in targeturl:
								white_dummy = 1
								break
				else:
					white_dummy = 1

				if black != ['']:	
					for x in black:
						if x in targeturl:


							black_dummy = 1
							break
				else:
					black_dummy = 0

				if white_dummy == 1 and black_dummy == 0:
					#time.sleep(random.randint(0,5))
					try:
						content = scrape(targeturl,URL)
						queue = queue + content[9]
					


						titletag = content[0]
						meta = content[1]
						H1 = content[3]

						titletag_count = count(titletag)
						meta_count = count(meta)
						body_count = content[2]
						H1_count = count(H1)
						wr.writerow([targeturl, content[8], titletag, meta, H1, titletag_count[0], meta_count[0],H1_count[0],body_count[0],body_count[1],content[4],content[5],content[6],content[7]])
					except:
						wr.writerow([targeturl,"NA","NA","NA","NA","NA","NA","NA","NA","NA","NA","NA","NA","NA","NA"])
					print(targeturl, 'success')

				else:
					pass
			myfile.flush()
			queue.pop(0)


def url_cleaner(url):

	if len(url)>0:
		if url[-1] != "/":
			url = url + "/"
	url_match = re.match("(https?://)?(.*?)\.(.*?)/",url)
	if url_match != None:
		if '.' not in url_match.group(3):
			return  url_match.group(2)+'.' +url_match.group(3)
		else:
			return url_match.group(3)



if __name__ == '__main__':
	analysis(sys.argv[1], sys.argv[2])

