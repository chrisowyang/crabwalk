from bs4 import BeautifulSoup
import requests
import csv
import nltk.data
from nltk.tokenize import RegexpTokenizer
import time
import re
import sys

def normalize(targeturl):
    targeturl = targeturl.replace("www.","")
    targeturl = targeturl.replace("http://","")
    targeturl = targeturl.replace("https://","")
    #targeturl = targeturl.replace("//","/")
    return targeturl

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



def last_directory(url):
    if url[-1] == "/":
        url = url[0:-1]
    reverse = url[::-1]
    for x in range(len(reverse)):
        if url[x] == "/":
            stop = x
            return url[:stop]+"/"
    return '/'
			

def process_links(full_link,targetURL,baseURL):
    
    clean_link = url_cleaner(full_link)
    
    domain = url_cleaner(baseURL)
    
    if '#' in full_link or len(full_link)<2:
        return 'ERROR'
    if clean_link == domain: #absolute link
        return normalize(full_link)
    
    elif "http" not in full_link: #internal link

        if full_link[0]=='/': #append to domain
            return baseURL+full_link
        elif full_link[0:2]=='./': #append to current directory
            return targetURL+full_link[2:]
        elif full_link[0:3]=='../':
                return 'ERROR'
        else: #append to last directory
            return last_directory(targetURL)+full_link
    else:
        return normalize(full_link) #external link



def scrape(targetURL,baseURL):
    """
    scrapes urls via BeautifulSoup recording title tags and h1 headers in addition to 
    """
    headers = {'User-Agent' : "Mozilla/5.0 (Windows NT 6.0; WOW64) AppleWebKit/534.24 (KHTML, like Gecko) Chrome/11.0.696.16 Safari/534.24"}
    
    start = time.time()

    end = targetURL[-10:]

    if "pdf" in end.lower():

        return ["NA","NA",[0,1,2],"NA","NA","NA","NA","NA","NA","NA","NA"]
    
    else:
        if "http" not in targetURL:
            targetURL = "http://" + targetURL
                
       
        r = requests.get(targetURL,headers=headers,timeout=15)

        stripped = r.text
        stripped = stripped.replace('\n', '. ')
    
        soup = BeautifulSoup(stripped,"html.parser")

        end_time = time.time()
        load_time = end_time - start
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
    
    
        links_list = []
        exlinks = 0
        inlinks = 0
        exlinks_cc = 0
        inlinks_cc = 0
        


        soup_links = soup.find_all('a', href=True)
        
        for link in soup_links:
            
            full_link=link.get('href')
            
            targetURL = normalize(targetURL)
            
            
            corrected_link = process_links(full_link, targetURL, baseURL) #fix relative links
                  
            corrected_link = normalize(corrected_link)
                    
            
            if corrected_link == 'ERROR':
                pass
                
            elif url_cleaner(corrected_link) == url_cleaner(baseURL):#if domains are the same, then internal
                  
                
                links_list.append(corrected_link)
                inlinks += 1
                inlinks_cc += len(full_link)
            
            else: #external links
                exlinks += 1
                exlinks_cc+= len(full_link)
            
    
        
        #BODY
        
        try:
            
            end = targetURL[-10:]
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

        #no follow
        if 'nofollow' in stripped or 'NOFOLLOW' in stripped or 'NoFollow' in stripped:
            nofollow = 1
        else:
            nofollow = 0
    

        content = [title, meta, text_count, H1, exlinks, inlinks, exlinks_cc, inlinks_cc,load_time, links_list, end_time, nofollow]
 

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
        wr.writerow(['URL','time stamp', 'load time', 'title tag text', 'meta tag text', 'h1 text','title tag count', 'meta description count','h1 count', 'body word count','body character count','ex links','in links','ex links cc','in links cc','no follow'])

        with open(basecsv,'rU') as fp:
            reader = csv.reader(fp,delimiter=",")
        
            for row in reader:
                rows.append(row)

            baseURL = rows[0][1]
            baseURL = normalize(baseURL)
            
            black = [x for x in rows[1][1:]]
            white = [x for x in rows[2][1:]]
            
            queue.append(baseURL)

                
                #queue of links to visit

            while len(queue)>0:
                
                targeturl = queue.pop(0)
                targeturl = normalize(targeturl)

                if targeturl not in visited: #check if link has been visited
                
                    visited.append(targeturl)#add to visited list
                                
                            #Does targeturl pass test parameters, white and black
                    white_dummy = 0 
                    black_dummy = 0 
                
                    if targeturl == baseURL: #both normalized; check if targeturl is the domain
                        white_dummy = 1 #passed white test
                        black_dummy = 0 #passed black test
                    else:
                        if white==['']: # white is empty
                            white_dummy = 1
                        else:  #make sure you don't have empty entries
                            for x in white:
                                x= normalize(x)
                                if x != '':
                                    if x in targeturl: #does target url pass white test?
                                        white_dummy = 1
                                        break #breaks out of for loop
                
                        if black==['']: #black is empty
                            black_dummy = 0; #passed black text
                        else:
                            for x in black:
                                x = normalize(x)
                                if x != '':
                                    if x in targeturl:
                                        black_dummy = 1 #failed black test
                                        break

                    
                    if white_dummy == 1 and black_dummy == 0:
                        try:
                            content = scrape(targeturl,baseURL) #both normalized
                             
                            queue = queue + content[9]
                            
                            titletag = content[0]
                            meta = content[1]
                            H1 = content[3]
                
                            titletag_count = count(titletag)
                            meta_count = count(meta)
                            body_count = content[2]
                            H1_count = count(H1)
                                      
                            wr.writerow([targeturl,content[10], content[8], titletag, meta, H1, titletag_count[0], meta_count[0],H1_count[0],body_count[0],body_count[1],content[4],content[5],content[6],content[7],content[11]])
                            
 
                        except:
                            print('ERROR',targeturl)
                
                    else:
                        pass
                    if len(visited)%5==0:
                        print('queue length:', len(queue))
                        print('visited:',len(visited))
                        print('percent complete',str(100-(100*len(queue)/(len(queue)+len(visited))))+"%")
                        print('---')
            print ("Done")  
                  
            fp.close()#close basecsv                       
        myfile.flush() #close output files
        myfile.close()

if __name__ == '__main__':
	analysis(sys.argv[1], sys.argv[2])

