### Clusterovani pomoci LDA na Spark ML
### Priklad na clusterovani knih Bible
# pyspark --master yarn --num-executors 8 --executor-memory 4G --executor-cores 2

import re
from pyspark.mllib.linalg import Vectors, SparseVector, DenseVector
from pyspark.mllib.clustering import LDA, LDAModel

### konstanty a parametry
K = 5 # pocet clusteru

################# pomocne funkce ######################
def verseUprav(verse):
    pom = verse.split('\t')
    hlava = pom[0]
    txt = pom[1]
    kniha = re.sub(r'^(\d?\D*)\d+:\d+', r'\1', hlava).strip()
    return (kniha, txt)

def slovoUprav(slovo):
    res = slovo.lower()
    res = re.sub(r'\W+', '', res)
    return res

def mergeDict(d1, d2):
    res = d1
    res.update(d2)
    return res

def startDict(d):
    return d

def Jaccard(v1, v2):
    return 1.0 * sum(map(min, zip(v1, v2))) / sum(map(max, zip(v1, v2)))

################### cteni a preprocessing dat ###########
# nacteni textu a uprava
bible = sc.textFile('data/bible.txt')
lines = bible.map(verseUprav) \
    .flatMap(lambda line: [(line[0], word) for word in line[1].split(' ')])
lines2 = lines.map(lambda line: (line[0], slovoUprav(line[1])))

# vyhozeni stopwords
sw = sc.textFile('/user/pascepet/data/stopwords.txt')
stopwords = set(sw.collect())
lines3 = lines2.filter(lambda line: not (line[1] in stopwords) and (line[1]!='')).cache()

# zjisteni unikatnich slov a vyhozeni slov s prilis malym vyskytem
slova = lines3.map(lambda line: (line[1],1))
slovaCet = slova.reduceByKey(lambda a, b: a+b) # zjisti se cetnosti
slovaUnik = slovaCet.filter(lambda w: w[1]>=10).keys().zipWithIndex().cache()
slovaUnikPocet = slovaUnik.count()
slovaVyber = set(slovaUnik.keys().collect())
lines3 = lines3.filter(lambda line: line[1] in slovaVyber)

# nahrazeni slova jeho ID
lines4 = lines3.map(lambda line: (line[1], line[0])) # prehodi se klic a hodnota
lines5 = lines4.join(slovaUnik) # pripoji se ID k nazvu knihy
lines6 = lines5.map(lambda line: line[1]) # a zahodi se slova jako klice - zustane nazev knihy jako klic 

# cetnosti slov (resp. jejich ID) po knihach
lines7 = lines6.map(lambda line: ((line[0], line[1]), 1))
wcts = lines7.reduceByKey(lambda a, b: a+b).cache()

wcts2 = wcts.map(lambda w: (w[0][0], {w[0][1]: w[1]})) # prevod na dictionary
bookDict = wcts2.combineByKey(startDict, mergeDict, mergeDict) # vytvoreni spolecneho dictionary pro kazdou knihu
corpus = bookDict.zipWithIndex() \
    .map(lambda x: [x[1], x[0]]) \
    .map(lambda book: [book[0], SparseVector(slovaUnikPocet, book[1][1])]) # korpus - RDD knih s jejich frekvencnimi slovniky

############## clustering ###############################
# Provede clusterovani do urceneho poctu temat pomoci LDA
bibleLdaModel = LDA.train(corpus, K)
	
# Vypise temata jako mnozinu nejdulezitejsich slov s vahami
bibleLdaModel.describeTopics(10) # Id deseti nejdulezitejsich slov pro kazde tema a jejich vahy  

# Ktera konkretni slova jsou nejdulezitejsi?
bibleTemata = bibleLdaModel.describeTopics(10)
slovaUnik.filter(lambda w: w[1] in bibleTemata[0][0]).collect()
slovaUnik.filter(lambda w: w[1] in bibleTemata[1][0]).collect()
slovaUnik.filter(lambda w: w[1] in bibleTemata[2][0]).collect()
slovaUnik.filter(lambda w: w[1] in bibleTemata[3][0]).collect()
slovaUnik.filter(lambda w: w[1] in bibleTemata[4][0]).collect()

# prirazeni knihy k tematu - napriklad pomoci vazene Jaccardovy podobnosti knihy a centroidu tematu
kniha = bookDict.filter(lambda b: b[0]=="John").first() # evangelium podle Jana
pomSum = sum(kniha[1].values())
indexy = kniha[1].keys()
relcet = [1.0*v/pomSum for v in kniha[1].values()]
pomRelcet = dict(zip(indexy, relcet)) # prevod absolutnich na relativni cetnosti
knihaRelcet = SparseVector(slovaUnikPocet, pomRelcet) # cetnosti slov ve vybrane knize

bibleTemataKomplet = bibleLdaModel.describeTopics() # kompletni info o centroidech - relativni cetnosti vsech slov
# cetnosti slov v tematu c. 2 (index 1)
indexy = bibleTemataKomplet[1][0]
relcet = bibleTemataKomplet[1][1]
tema1Relcet = SparseVector(slovaUnikPocet, dict(zip(indexy, relcet)))
# cetnosti slov v tematu c. 5 (index 4)
indexy = bibleTemataKomplet[4][0]
relcet = bibleTemataKomplet[4][1]
tema4Relcet = SparseVector(slovaUnikPocet, dict(zip(indexy, relcet)))
# porovnani vybrane knihy s vybranymi tematy - podobnost knihy a centroidu
Jaccard(list(DenseVector(knihaRelcet)), list(DenseVector(tema1Relcet)))
Jaccard(list(DenseVector(knihaRelcet)), list(DenseVector(tema4Relcet)))
