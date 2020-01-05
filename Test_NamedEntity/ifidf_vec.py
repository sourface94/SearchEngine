#!/usr/bin/python3
# 
import sys
import math
import json
import nltk

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
	answer = retrieve_vector(query_terms)	# comment out for part 2

	print ('Query: ', query_terms)
	i = 0
	for docid in answer:
		i += 1
		print (i, docids[docid])
		if i == 10:
			break

						
	
def retrieve_vector(query_terms):
	## a function to perform vector model retrieval with tf*idf weighting
	#
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
	
	#### your code starts here ####
	
	##################################################################################################
	parse_tree = nltk.ne_chunk(nltk.tag.pos_tag(query_terms.split()), binary=True)
	for t in parse_tree.subtrees():
		#print(t)
		if t.label() == 'NE':	
			# named_entities.append(t)		# saves a tree
			named_entities.append(list(t))  # saves a list of tagged words instead of a tree
			
	found_entities = []
	for ne in named_entities:
		entity = ''
		#print(ne)
		for e in ne:
			entity += e[0]+' '
		entity = entity.strip()
		query_terms = query_terms.replace(entity, '')
		found_entities.append(entity)
		
	#idf values
	idfs = idf(query_terms)
	termidfs = idf(found_entities)
	idfs.extend(termidfs)
	##################################################################################################
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
	
	##################################################################################################
		
	for entity in found_entities:
		if entitiy in vocab:
			qtermtf = 1/len(query_terms) #tf for query
			qweight = qtermtf*idfs[termumber] #weight of query term
			qweights.append(qweight)
			cummulativeqweight += qweight #add to the cummulativ weight for the query
			cummulativeqweightsq += qweight*qweight
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
				
				#create vector for each doc
				docvector = weights.get(docid)
				if docvector == None:
					weights[docid] = [weight]
				else:
					docvector.append(weight)
				
				if docid not in cummulativeweight: # add to the cumulative weights
					cummulativeweight[docid] = weight
					cummulativeweightsq[docid] = weight*weight
				else:
					cummulativeweight[docid] += weight
					cummulativeweightsq[docid] += weight*weight
			termumber += 1
	
	##################################################################################################
	
	for term in query_terms:	
		if term in vocab:
			qtermtf = 1/len(query_terms) #tf for query
			qweight = qtermtf*idfs[termumber] #weight of query term
			qweights.append(qweight)
			cummulativeqweight += qweight #add to the cummulativ weight for the query
			cummulativeqweightsq += qweight*qweight
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
				
				#create vector for each doc
				docvector = weights.get(docid)
				if docvector == None:
					weights[docid] = [weight]
				else:
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
	#for w, d in weights.items():
		#print('docid: ', w, ' veclength: ', len(d))
	#print(answer)	
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
