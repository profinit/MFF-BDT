### Priklad 1: word count

# nacteni RDD
lines = sc.textFile("/user/pascepet/data/bible.txt")

# rozdeleni radku
words = lines.flatMap(lambda line: line.split(" "))

# transformace radku na (key, value)
pairs = words.map(lambda word: (word, 1))

# secteni jednicek ke kazdemu klici
counts = pairs.reduceByKey(lambda a, b: a + b)

