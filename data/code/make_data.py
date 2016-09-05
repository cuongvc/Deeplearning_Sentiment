import codecs
import re
import numpy as np
from collections import defaultdict
import time
windowsize = 5

file_data = "./../kinh_te_version_4.txt"
domain = 'kinhte'

file_lexicon = 'Lexicon_WordList.txt'
file_reserve = 'swapword.txt'

# file_data = "./../du_lich_version_1.txt"
# domain = 'dulich'

# file_data = "./../kinh_te_version_4.txt"
# domain = 'kinhte'

file_dictionary = "./data_" + domain + "/dictionary.txt"
fileW2VFull = "./vector-new-skipgram-filtered"
fileW2VSmall = "./data_" + domain + "/w2vFile.txt"
file_windowsize = "./data_" + domain + "/full_all_windowsize_file.txt"
file_sentiment = "./data_" + domain + "/full_all_label_file.txt"
file_sentiment_string = "./data_" + domain + "/full_all_label_string_file.txt"

label_sentiment = {'positive' : 0, 'neutral' : 1, 'negative' : 2}

def read_lexicon():
	dictLexicon = {}
	fLexicon = codecs.open(file_lexicon, "r", "utf-8")
	for line in fLexicon:
		label = line.split('\t')[0]
		word = line.split('\t')[1]
		dictLexicon[word] = int(label)
	return dictLexicon

def read_reverse():
	dictReverse = {}
	fReverse = codecs.open(file_reserve, "r", "utf-8")
	for line in fReverse:
		word = line.split('\t')[0]
		dictReverse[word] = 1
	return dictReverse

def make_dict():
	# read data and make dictionary
	dictionary = {}
	fDataRaw = codecs.open(file_data, "r", "utf-8")
	for line in fDataRaw:
		array = line.split('\t')
		# print line
		if (len(array) > 1):
			if array[0] not in dictionary:
				dictionary[array[0].lower()] = len(dictionary)
	# print(len(dictionary))
	dictionary["spec_none"] = len(dictionary)

	# write dictionary to file
	fDictionary = codecs.open(file_dictionary, "w", "utf-8")
	i = 0;
	for word in dictionary:
		i += 1
		if (i == len(dictionary)):
			fDictionary.write(word)	
		else:
			fDictionary.write(word + "\n")
	fDictionary.close()
	return dictionary

def create_random_vector(dim):
	vecString = ""
	vec = np.random.rand(dim)
	for i in range(0, len(vec)):
		if i == len(vec) - 1:
			vecString += str(vec[i])
		else:	
			vecString += str(vec[i]) + " "
	return vecString

def make_vector_w2v_small(dictLexicon, dictReverse, dictionary):
	# make vector w2v smaller to keep only word is appeaded in dictionary
	fW2VFull = codecs.open(fileW2VFull, "r", "utf-8")
	fW2VSmall = codecs.open(fileW2VSmall, "w", "utf-8")
	w2vSmall = {}
	for line in fW2VFull:
		args = line.strip().split(" ")
		word = args[0]
		vector = " ".join([str(x) for x in args[1:]])
		if word.lower() in dictionary:
			w2vSmall[word.lower()] = vector
	w2vSmall['spec_none'] = create_random_vector(len(args) - 1)
	i = 0
	for word in dictionary:
		i += 1
		sentiWordStr = ''
		if word in dictLexicon:
			if dictLexicon[word] == 1:
				sentiWordStr += '1.0 0.0 '
			else:
				sentiWordStr += '0.0 1.0 '
			if word == 'hay':
				print("hay sentiWordStr : " + sentiWordStr)
		else:
			sentiWordStr += '0.0 0.0 '
		if word in dictReverse:
			sentiWordStr += '1.0'
		else:
			sentiWordStr += '0.0'
		if word in w2vSmall:
			if i == len(dictionary):
				fW2VSmall.write(w2vSmall[word] + ' ' + sentiWordStr)
			else:
				fW2VSmall.write(w2vSmall[word] + ' ' + sentiWordStr + '\n')			
		else:
			if i == len(dictionary):
				fW2VSmall.write(w2vSmall["spec_none"] + ' ' + sentiWordStr)
			else:
				fW2VSmall.write(w2vSmall["spec_none"] + ' ' + sentiWordStr + '\n')
	fW2VFull.close()
	fW2VSmall.close()
	return w2vSmall

def make_vectorWindowSize(dictLexicon, dictReverse, dictionary, words, i):
	# vector is string contains list index of word in a windowsize
	vectorWindowSize = ""
	# tmpVector = ""
	if i >= windowsize:
		for j in range(i - windowsize, i):
			vectorWindowSize += str(dictionary[words[j]]) + " "
			# tmpVector += words[j] + " "
	else:
		for j in range(0, windowsize - i):
			vectorWindowSize += str(len(dictionary) - 1) + " "
			# tmpVector += str(dictionary[len(dictionary) - 1]) + " "
		for j in range(0, i):
			vectorWindowSize += str(dictionary[words[j]]) + " "					
			# tmpVector += words[j] + " "
	vectorWindowSize += str(dictionary[words[i]]) + " "
	# tmpVector += words[i] + " "
	if len(words) - 1 - i >= windowsize:
		for j in range(i+1, i + windowsize + 1):
			vectorWindowSize += str(dictionary[words[j]]) + " "
			# tmpVector += words[j] + " "
	else:
		for j in range(i+1, len(words)):
			vectorWindowSize += str(dictionary[words[j]]) + " "
			# tmpVector += words[j] + " "
		for j in range(0, windowsize - (len(words) - 1 - i)):
			vectorWindowSize += str(len(dictionary) -1 ) + " "
			# tmpVector += str(dictionary[len(dictionary) - 1]) + " "

	vectorWindowSize = vectorWindowSize[:-1]
	# print(tmpVector)
	# print(vectorWindowSize)
	# print(len(vectorWindowSize.split(' ')))
	# print(words)
	# print(i)
	# print('\n')

	return vectorWindowSize

# Make vector present a Term/Aspect by windowsize

def make_windowsize(dictLexicon, dictReverse, dictionary):
	fDataRaw = codecs.open(file_data, "r", "utf-8")
	fWindowsize = codecs.open(file_windowsize, "w", "utf-8")
	fSentiment = codecs.open(file_sentiment, "w", "utf-8")
	fSentimentString = codecs.open(file_sentiment_string, "w", "utf-8")
	words = []
	ners = []
	sentiments = []
	index = 0
	numLine = 0
	for line in fDataRaw:
		numLine += 1
		# print("numLine : " + str(numLine))
		line = line.replace('\n', '')
		line = line.replace('\r', '')
		array = line.split('\t')
		if (len(array) > 1):
			word = array[0]
			if not word in dictionary:
				word = "spec_none"
			words.append(word)
			ners.append(array[1])
			if len(array) > 2:
				sentiments.append(array[2])
			else:
				sentiments.append("non-senti")
		else:
			for i in range(0, len(words)):
				# print(words[i])
				if sentiments[i] != "non-senti":
					# print(sentiments[i])
					vectorWindowSize = make_vectorWindowSize(dictLexicon, dictReverse, dictionary, words, i)
					if index == 0:
						index += 1
						fWindowsize.write(vectorWindowSize)
						fSentimentString.write(sentiments[i])
						fSentiment.write(str(label_sentiment[sentiments[i]]))
					else:
						fWindowsize.write('\n' + vectorWindowSize)
						fSentimentString.write('\n' + sentiments[i])
						fSentiment.write('\n' + str(label_sentiment[sentiments[i]]))
			# time.sleep(5.5)    # pause 5.5 seconds
			words = []
			ners = []
			sentiments = []
	fSentiment.close()
	fSentimentString.close()
	fWindowsize.close()
	

def make_cross_validation():
	fTestLabel = codecs.open('./data_' + domain + '/full_test_label_file.txt', 'w', 'utf-8')
	fTrainLabel = codecs.open('./data_' + domain + '/full_train_label_file.txt', 'w', 'utf-8')
	fTestWindowSize = codecs.open('./data_' + domain + '/full_test_windowsize_file.txt', 'w', 'utf-8')
	fTrainWindowSize = codecs.open('./data_' + domain + '/full_train_windowsize_file.txt', 'w', 'utf-8')
	fAllLabel = codecs.open('./data_' + domain + '/full_all_label_file.txt', 'r', 'utf-8')
	fAllWindowSize = codecs.open('./data_' + domain + '/full_all_windowsize_file.txt', 'r', 'utf-8')

	for lineLabel in fAllLabel:
		lineWindowsize = fAllWindowSize.readline()
		numrand = np.random.randint(0, 10)
		if numrand == 0:
			fTestLabel.write(lineLabel)
			fTestWindowSize.write(lineWindowsize)
		else:
			fTrainLabel.write(lineLabel)
			fTrainWindowSize.write(lineWindowsize)
	fTrainLabel.close()
	fTrainWindowSize.close()
	fTestLabel.close()
	fTestWindowSize.close()
	fAllLabel.close()
	fAllWindowSize.close()

if __name__ == "__main__":
	dictionary = make_dict()
	dictLexicon = read_lexicon()
	dictReverse = read_reverse()
	make_vector_w2v_small(dictLexicon, dictReverse, dictionary)
	make_windowsize(dictLexicon, dictReverse, dictionary)
	make_cross_validation()