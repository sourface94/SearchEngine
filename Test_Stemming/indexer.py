#!/usr/bin/python3

import sys
import re
import json
from stemming.porter2 import stem

# global declarations for doclist, postings, vocabulary and doccount
docids = [] #contains documents
postings = {} #contains the words each document occurs in, with the number of times each word occurs
vocab = [] #contains all the words from every document
doccount = [] #contains number of words in each docuemnt

# main is used for offline testing only
def main():
	# code for testing offline
	if len(sys.argv) != 2:
		print ('usage: ./indexer.py file')
		sys.exit(1)
	filename = sys.argv[1]

	try:
		input_file = open(filename, 'r')
	except (IOError) as ex:
		print('Cannot open ', filename, '\n Error: ', ex)

	else:
		page_contents = input_file.read() # read the input file
		url = 'http://www.'+filename+'/'
		#print (url, page_contents)
		make_index(url, page_contents)
		write_index()
	finally:
		input_file.close()
	
	
def write_index():
	# write index data to files at end of crawl
	# data is used for retrieval
	
	# declare refs to global variables
	global docids
	global postings
	global vocab
	global doccount
	
	outlist1 = open('docids.txt', 'w')
	outlist2 = open('vocab.txt', 'w')
	outlist3 = open('postings.txt', 'w')
	outlist4 = open ('doclength.txt', 'w')
	
	#write global variables to text files
	json.dump(docids, outlist1)
	json.dump(vocab, outlist2)
	json.dump(postings, outlist3)
	json.dump(doccount, outlist4)
	
	outlist1.close()
	outlist2.close()
	outlist3.close()
	outlist4.close()
	return
	
def clean_html(page_contents):
	# function to clean html 
	#removes script, style and html tags
	cleanedSite = re.sub(r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>', '', page_contents.strip())
	cleanedSite = re.sub(r'<style\b[^<]*(?:(?!<\/style>)<[^<]*)*<\/style>', '', cleanedSite)
	#removes comments
	cleanedSite = re.sub(r"(?s)<!--(.*?)-->[\n]?", "", cleanedSite)
	#removes regular html tags
	cleanedSite = re.sub(r'<[^>]+>', '', cleanedSite)
	#removes punctution and other special characters
	cleanedSite = re.sub(r'[^\w\s]', '', cleanedSite)
	#removes whitespace
	cleanedSite = re.sub(r"&nbsp;", " ", cleanedSite)
	cleanedSite = re.sub(r"\t", " ", cleanedSite)
	cleanedSite = re.sub(r"[ ]+", " ", cleanedSite)
	# removes blank lines
	cleanedSite = re.sub(r"[ ]*\n", "\n", cleanedSite)
	cleanedSite = re.sub(r"\n+", "\n", cleanedSite) 
	cleaned = cleanedSite.strip()
	
	return cleaned	
	
def make_index(url, page_contents):
	# parameters are the URL and raw page contents from crawler
	
	# declare refs to global variables
	global docids		# contains URLs + docids
	global postings		# contains postings information
	global vocab		# contains words + wordids
	global doccount	
	
	# first convert bytes to string if necessary
	if (isinstance(page_contents, bytes)): 
		page_contents = page_contents.decode('utf-8')
	else:
		page_contents = page_contents

	print ('===============================================')
	print ('make_index: url = ', url)
	print ('===============================================')

	#edit the url so that it only contais the domain
	if (re.search('http://', url)):
		domain = re.sub('http://', '', url)
	elif (re.search('https://', url)):
		domain = re.sub('https://', '', url)	
	if (re.search('www.', domain)):
		domain = re.sub('www.', '', domain)
	
	#add the domain to docids
	if domain not in docids:
		docids.append(domain)
	docid = int(docids.index(domain))
	
	#add each term to vocab and postings
	wordcount = 0 # number of words in the document
	termid = 0
	page_text = clean_html(page_contents)
	stemmedtext = ''
	for word in page_text.split():
		word = stem(word)
		stemmedtext += ' '
		stemmedtext += word
	
	for term in stemmedtext.split():
		#increment the word counter for the document
		wordcount += 1
		#add teach term to vocabs
		term = term.lower()		
		if term in vocab:
			termid = int(vocab.index(term))
		else:
			vocab.append(term)
			termid = int(vocab.index(term))
		
		#add each term with its docid to postings with the 
		#frequency the term appears in the document
		values = postings.get(termid)	
		if values == None:
			#term is not in postings so  
			#add it to postings with docid and freqency
			postings[termid] = [[docid, 1]]
		else:
			##add docid and frequency to postings
			found = False
			for val in values:
				if val[0] == docid:
					val[1] += 1					
					found = True
					break
			if found == False:
				values.append([docid, 1])
				
	#add the wordcount for the document to doccount
	if docid  >= len(doccount):
		doccount.append(wordcount)
	else:
		doccount[docid] = wordcount
		
	#calls function which writes docids, 
	#vocab, postings and doccount to file
	write_index()	
	return
	
	
	
# Standard boilerplate to call the main() function
if __name__ == '__main__':
    main()	