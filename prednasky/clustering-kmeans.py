### Clustering pomoci K-means na Spark ML
### priklad na umelych datech - 1M bodu, 4 dimenze

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
clusteredData.take(20)
clusteredData.map(lambda x: (x[0],1)).reduceByKey(lambda a,b:a+b).take(6)
