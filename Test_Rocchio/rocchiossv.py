#!/usr/bin/python3
# 
import sys
import math
import json
from stemming.porter2 import stem

docids = []
doclength = []
vocab = []
postings = {}
def main():
	# code for testing offline	
	if len(sys.argv) < 2:
		print ('usage: ./retriever.py term [term ...]')
		sys.exit(1)
	query_terms = sys.argv[1:]

	answer = []
	answer = retrieve_vector(query_terms)

	print ('Query: ', query_terms)
	i = 0
	for docid in answer:
		i += 1
		print (i, docids[docid]) 	


def retrieve_vector(query_terms):
	## a function to perform vector model retrieval with tf*idf weighting
	#
	from operator import add	# for vector addition

	global docids		# list of doc names - the index is the docid (i.e. 0-4)
	global doclength	# number of terms in each document
	global vocab		# list of terms found (237) - the index is the termid
	global postings		# postings dictionary; the key is a termid
						# the value is a list of postings entries, 
						# each of which is a list containing a docid and frequency
						
	f = open("vocab.txt")
	vocab = json.load(f)
	f = open("doclength.txt")
	doclength = json.load(f)
	f = open("docids.txt")
	docids = json.load(f)
	f = open("postings.txt")
	postings = json.load(f)
	answer = []
	#### your code starts here ####
	
	
	relfbkmax = 3		# the number of docs to consider for Rocchio
	alpha = 0.75		# Rocchio weight for original query
	beta = 0.25			# influence of relevant docs
	gamma = 0			# influence of irrelevant docs

	#f = open("postings.txt")
	#postings = json.load(f)
	
	#### your code starts here ####	
	stemmedterms = []
	for term in query_terms:
		term = stem(term)
		stemmedterms.append(term)
	query_terms = stemmedterms
	
	#### your code starts here ####
	#idf values
	idfs = idf(query_terms)
	
	#dictionary to contains the tfs
	tfs = {}
	#all documents that contain any of the words in the query
	docsused = []
	
	
	
	#weights for terms 
	weights = {}
	#cummaltive weights
	cummulativeqweight = 0
	cummulativeqweightsq = 0
	cummulativeweight = {}
	cummulativeweightsq = {}
	qweights = []
	termumber = 0;
	for term in query_terms:	
		if term in vocab:
			qtermtf = 1/len(query_terms) #tf for query
			qweight = qtermtf*idfs[termumber] #weight of query term
			qweights.append(qweight)
			cummulativeqweight += qweight #add to the cummulativ weight for the query
			cummulativeqweightsq += qweight*qweight
			tfdocs = [] #documents that contain the terms in the query
			termid = int(vocab.index(term))
			values = postings.get(str(termid)) #get postings list for the term
			#for each tuple in postings
			for val in values:
				#docid in tuple
				docid = val[0]
				
				#add document to docsused
				if docid not in docsused: 
					docsused.append(docid)
					
				#calculate tf*idf/weights			
				termcount = val[1] #number of times term occurs	
				documentLength = doclength[docid]
				tf = termcount/documentLength
				weight = tf*idfs[termumber]
				
				#create vector for each doc and make sure they are all the
				#same length
				docvector = weights.get(docid)
				if docvector == None:
					if termnumber == 0:
						weights[docid] = [weight]
					else:
						weights[docid] = 0
						docvector = weights.get(docid)
						for i in range (0, termnumber-1):
							docvector.append(0)
						docvector.append(weight)
					###need code here
				else:
					if len(docvector) != termnumber:
						for i in range (0, termnumber-1):
							docvector.append(0)
					docvector.append(weight)
				
				if docid not in cummulativeweight: # add to the cumulative weights
					cummulativeweight[docid] = weight
					cummulativeweightsq[docid] = weight*weight
				else:
					cummulativeweight[docid] += weight
					cummulativeweightsq[docid] += weight*weight
			termumber += 1
	
	cossimilarities = []
	#print('cumualtive wight dict: ')
	#for doc, weight in cummulativeweight.items():
	#	print(doc, weight)
	for doc, weight in cummulativeweight.items():
		#print('cummulativeqweight: ', cummulativeqweight)
		#print('weight: ', weight)
		numerator = cummulativeqweight*weight
		#print('numerator', numerator)
		cumMultiplied = cummulativeqweightsq*cummulativeweightsq.get(doc)	
		denominator = math.sqrt(cumMultiplied)
		#print('denominator', denominator)
		if denominator == 0:
			distance = 0
		else:
			distance = numerator/denominator
		#docname = docids[doc]
		cossimilarities.append([doc, distance])
	
	cossimilarities = sorted(cossimilarities, key=lambda x: x[1], reverse=True)
	#for i in cossimilarities:
		#print(i)
	answer = [i[0] for i in cossimilarities]
	
########################################################################################
	##Rocchio implemented now
	topResults = int(len(answer)/23)
	relevantDocuments = answer[:topResults]
	irrelevantDocuments = answer[topResults+1:]
	for qtermweight in qweights:
		qtermweight = qtermweight*alpha
		
	oneOverRelDoc = beta*(1/(len(relevantDocuments)))
	oneOverIrrelDoc = gamma*(1/len(irrelevantDocuments))
	
	#relevant vector summation
	relevantVector = []
	for doc in relevantDocuments:
		docvector = weights.get(doc)
		for r in range(1, len(docvector)+1):
			if len(relevantVector) < r:
				relevantVector.append(docvector[r-1])
			else:
				relevantVector[r-1] += docvector[r-1]
				
	for weight in relevantVector:
		weight = weight*oneOverRelDoc
	
	#irrelevant vector summation	
	irrelevantVector = []
	for doc in irrelevantDocuments:
		docvector = weights.get(doc)
		for r in range(1, len(docvector)+1):
			if len(irrelevantVector) < r:
				irrelevantVector.append(docvector[r-1])
			else:
				irrelevantVector[r-1] += docvector[r-1]
	
	for weight in irrelevantVector:
		weight = weight*oneOverIrrelDoc
	
	#minus the irrelevant vector from the relevant vector
	for r in range(1, len(irrelevantVector)+1):
			if len(relevantVector) < r:
				relevantVector.append(irrelevantVector[r-1]*-1)
			else:
				relevantVector[r-1] -= irrelevantVector[r-1]
	
	#add original query vector to vector from rest of forumla	
	for r in range(1, len(relevantVector)+1):
			if len(qweights) < r:
				qweights.append(relevantVector[r-1])
			else:
				qweights[r-1] += relevantVector[r-1]
				
########################################################################################	
	roccummulativeqweight = 0
	roccummulativeqweightsq = 0
	for weight in qweights:
		roccummulativeqweight +=weight
	for weight in qweights:
		roccummulativeqweightsq += weight*weight
		
	cossimilarities = []
	#print('cumualtive wight dict: ')
	#for doc, weight in cummulativeweight.items():
	#	print(doc, weight)
	for doc, weight in cummulativeweight.items():
		#print('cummulativeqweight: ', cummulativeqweight)
		#print('weight: ', weight)
		numerator = roccummulativeqweight*weight
		#print('numerator', numerator)
		cumMultiplied = roccummulativeqweightsq*cummulativeweightsq.get(doc)	
		denominator = math.sqrt(cumMultiplied)
		#print('denominator', denominator)
		if denominator == 0:
			distance = 0
		else:
			distance = numerator/denominator
		#docname = docids[doc]
		cossimilarities.append([doc, distance])
	
	cossimilarities = sorted(cossimilarities, key=lambda x: x[1], reverse=False)
	#for i in cossimilarities:
		#print(i)
	answer = [i[0] for i in cossimilarities]
	
	#### your code ends here ####	
	return answer

def idf(query_terms):
	idfs = []
	docInCollection = len(docids)
	#print('docInCollection', docInCollection)
	for term in query_terms:
		if term in vocab:			
			termid = int(vocab.index(term))
			values = postings.get(str(termid))
			docContainingTerm = len(values)
	#		print('docContainingTerm', docContainingTerm)
			term_idf = math.log10(docInCollection/docContainingTerm)
	#		print('term_idf: ', term_idf)
			idfs.append(term_idf)
	#for i in idfs:
	#	print(i)
	return idfs		

	# Standard boilerplate to call the main() function
if __name__ == '__main__':
    main()
