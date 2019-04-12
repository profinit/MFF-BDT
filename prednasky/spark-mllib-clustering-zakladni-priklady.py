###### Clustering on Spark ML - zakladni priklady #######

### k-means on Spark ML
# pyspark --master yarn --num-executors 2 --executor-memory 4G

from pyspark.mllib.clustering import KMeans, KMeansModel
from numpy import array

# Nacte a upravi data
data = sc.textFile("data/clustering/kmeans_data2.csv")
parsedData = data.map(lambda line: array([float(x) for x in line.split(' ')]))
parsedData.cache()

# Vyzkousi ruzne pocty clusteru a spocita soucet ctvercu odchylek
for ki in range(1, 11):
    modelKM = KMeans.train(parsedData, ki, maxIterations=10, runs=10, initializationMode="random")
    WSSSE = modelKM.computeCost(parsedData) # soucet ctvecovych odchylek uvnitr clusteru
    print("K="+str(ki)+" | Within Set Sum of Squared Error = " + str(WSSSE))

# --> k=6 (od sesti vys uz WSSSE klesa pomalu)
kmCount = 6
modelKM = KMeans.train(parsedData, kmCount, maxIterations=10, runs=10, initializationMode="random")
modelKM.clusterCenters
# prirazeni cisla clusteru k jednotlivym radkum
clusteredData = parsedData.map(lambda x: (modelKM.predict(x), x))


### Latent Dirichlet Allocation on Spark ML

from pyspark.mllib.clustering import LDA, LDAModel
from pyspark.mllib.linalg import Vectors

# Nacte a upravi data
data = sc.textFile("data/clustering/sample_lda_data_basic.txt")
parsedData = data.map(lambda line: Vectors.dense([float(x) for x in line.strip().split(' ')]))

# Ke kazdemu radku se prida unikatni ID jako index
corpus = parsedData.zipWithIndex().map(lambda x: [x[1], x[0]]).cache()

# Provede clusterovani do urceneho poctu temat pomoci LDA
ldaModel = LDA.train(corpus, k=3)

# Vypise temata jako centroidy - souradnice centroidu jsou soucty cetnosti
print("Learned topics (as distributions over vocab of " + str(ldaModel.vocabSize()) + " words):")
topics = ldaModel.topicsMatrix()
for topic in range(3):
    print("Topic " + str(topic) + ":")
    for word in range(0, ldaModel.vocabSize()):
        print(" " + str(topics[word][topic]))
		
# Vypise temata jako mnozinu nejdulezitejsich slov s vahami
ldaModel.describeTopics(3) # tri nejdulezitejsi slova a jejich vaha  

# Prirazeni dokumentu k tematum
# napr. pomoci vazene Jaccardovy podobnosti - viz samostatny priklad


### Power Iteration Clustering on Spark ML

from pyspark.mllib.clustering import PowerIterationClustering, PowerIterationClusteringModel

# Load and parse the data
data = sc.textFile("data/clustering/pic_data_basic2.txt") # upraveny puvodni priklad
similarities = data.map(lambda line: line.split(' ')) \
    .map(lambda x: (int(x[0]), int(x[1]), float(x[2])))

# Cluster the data into two classes using PowerIterationClustering
model = PowerIterationClustering.train(similarities, 2, 20) # na Metacentru nefunguji velke hodnoty maxIteration

model_res = model.assignments().map(lambda x: (x.id, x.cluster)) \
    .sortBy(lambda x: x[1])

