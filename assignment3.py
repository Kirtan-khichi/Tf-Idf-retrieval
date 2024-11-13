import os
import math


folderPath = "25"



def tagValueFinder(text, tag):
    """
    This function find the Value between the given tag.
    """
    startIndex = text.find(f'<{tag}>')
    endIndex = text.find(f'</{tag}>')

    return text[startIndex + len(tag) + 2 : endIndex]

def fileReader(folderPath):
    """
    This function reads the folder documents and create a dictionary of DOCNO to ID.
    """
    docIdDic = {}
    textFiles = []
    i = 1
    for file in os.listdir(folderPath):
        with open(folderPath+ "\\" + file, "r+") as f:
            text = f.read()
            docIdDic[tagValueFinder(text, "DOCNO")] = i
            textFiles.append(text)

        i += 1

    return docIdDic, textFiles

def _is_valid_token(token):
    return token.isalnum() or token == "_"


def tokenizer(text):
    """
    This function tokenize the text into tokens 
    """
    text = text.lower()
    tokens = []

    temp = ""
    for i in text:
        if _is_valid_token(i):
            temp += i

        elif not _is_valid_token(i) and not len(temp) == 0:
            tokens.append(temp)
            temp = ""

    return tokens


documentTokens = {}
TokensDic = {}
i = 0

for doc in fileReader(folderPath)[1]:
    documentId = tagValueFinder(doc, "DOCNO")
    documentTextTokens = tokenizer(tagValueFinder(doc, "TEXT"))
    documentTitleTokens = tokenizer(tagValueFinder(doc, "TITLE"))

    documentTokens[documentId] = (documentTitleTokens + documentTextTokens)

    for token in (documentTitleTokens + documentTextTokens):
        if token not in TokensDic:
            TokensDic[token] = i
            i += 1


def idf(docList, tokenDic):
    documentFrequencyDic = {}

    for token in tokenDic.keys():
        for doc in docList:
            if token in doc:
                if token in documentFrequencyDic:
                    documentFrequencyDic[token] += 1

                else:
                    documentFrequencyDic[token] = 1
                        
    idfDic = {}
    totalDocs = len(docList)

    for term, freq in documentFrequencyDic.items():
        # print(freq, term)
        # break
        idfDic[term] = math.log(totalDocs / freq)

    return idfDic

def tf(docList):
    documentTermsDic = {}

    for doc in docList:

        docDict = {}
        documentId = tagValueFinder(doc, "DOCNO")
        documentTextTokens = tokenizer(tagValueFinder(doc, "TEXT"))
        documentTitleTokens = tokenizer(tagValueFinder(doc, "TITLE"))

        tokens =  (documentTitleTokens + documentTextTokens)

        for token in tokens:
            if token in docDict:
                docDict[token] += 1

            else:
                docDict[token] = 1

        documentTermsDic[documentId] = docDict

    return documentTermsDic

def tfIdf(docList, TokensDic):

    tfIdfDic = {}
    
    TF = tf(docList)
    IDF = idf(docList, TokensDic)

    for doc in docList:

        documentId = tagValueFinder(doc, "DOCNO")
        temp = {}
        for token, value in TF[documentId].items():
            try:
                idfValue = IDF[token]

                temp[token] = value * idfValue
            except:
                pass

        tfIdfDic[documentId] = temp

    return tfIdfDic

tfIdfDIC = tfIdf(fileReader(folderPath)[1], TokensDic)


def pairWiseSimilarity(doc1, doc2, tf_idf):
    documentId1 = tagValueFinder(doc1, "DOCNO")
    documentTextTokens1 = tokenizer(tagValueFinder(doc1, "TEXT"))
    documentTitleTokens1 = tokenizer(tagValueFinder(doc1, "TITLE"))

    documentId2 = tagValueFinder(doc2, "DOCNO")
    documentTextTokens2 = tokenizer(tagValueFinder(doc2, "TEXT"))
    documentTitleTokens2 = tokenizer(tagValueFinder(doc2, "TITLE"))

    tfIdfValue1 = tf_idf.get(documentId1, {})
    tfIdfValue2 = tf_idf.get(documentId2, {})

    magnitudeOfDoc1 = sum(value ** 2 for value in tfIdfValue1.values()) ** 0.5
    magnitudeOfDoc2 = sum(value ** 2 for value in tfIdfValue2.values()) ** 0.5

    dot_product = sum(tfIdfValue1.get(token, 0) * tfIdfValue2.get(token, 0) for token in set(documentTextTokens1 + documentTitleTokens1))

    similarity = dot_product / (magnitudeOfDoc1 * magnitudeOfDoc2) if magnitudeOfDoc1 * magnitudeOfDoc2 != 0 else 0

    return similarity

docList = fileReader(folderPath)[1]


def documentsSimilarityMatrix(docList, tf_idf):

    similarityDict = {}

    for i in range(len(docList)):
        for j in range(len(docList)):
            if i != j:

                doc1 = docList[i]
                doc2 = docList[j]

                documentId1 = tagValueFinder(doc1, "DOCNO")
                documentId2 = tagValueFinder(doc2, "DOCNO")

                similarityScore = pairWiseSimilarity(doc1, doc2, tf_idf)

                similarityDict[f"{documentId1}_{documentId2}"] = similarityScore

    return similarityDict

scores = documentsSimilarityMatrix(docList, tfIdfDIC)


def ranking(scores):

    scoresList = sorted(list(scores.values()), reverse=True)[0:50]
    i = 0
    for term, value in scores.items():
        if value in scoresList:
            temp = term.split("_")
            i += 1
            print("Similarity score between document id", temp[0], "and", temp[1], "is", value)

ranking(scores)