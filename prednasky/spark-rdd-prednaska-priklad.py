### Priklad 1: word count

# nacteni RDD
lines = sc.textFile("/user/pascepet/data/bible.txt")

# rozdeleni radku
words = lines.flatMap(lambda line: line.split(" "))

# transformace radku na (key, value)
pairs = words.map(lambda word: (word, 1))

# secteni jednicek ke kazdemu klici
counts = pairs.reduceByKey(lambda a, b: a + b)



### Priklad 2: podobnost obrazku

# rozparsuje BMP soubor - velmi zjednodusene
# predem vime, ze soubor je 4x4 pixely a kodovani je pouze 0x00 = cerna, 0xFF = bila
# vrati poslednich 16 bytu prevedenych na 0/1 (0 = bila, 1 = cerna)
def parseBMP(file):
    name = file[0]
    bytes = file[1]
    bytesLast = bytes[-16:]
    bits = []
    for z in bytesLast:
        if z=='\x00':
            bits.append(1)
        elif z=='\xff':
            bits.append(0)
        else:
            pass
    return (name, bits)

# pocita podobnost mezi dvema bitmapami jako podil shodnych bitu ze vsech
def similarity(bits, pattern=[0]*16):
    sum = 0
    for i in range(0, len(bits)):
        sum += (bits[i]==pattern[i])
    return sum*1.0/len(bits)

def similPair(pair):
    file1 = pair[0]
    file2 = pair[1]
    return (file1[0], file2[0], similarity(file1[1], file2[1]))

files = sc.binaryFiles('/user/pascepet/data/pismena/*.bmp')
filesParsed = files.map(parseBMP)
filesPairs = filesParsed.cartesian(filesParsed).filter(lambda f: f[0][0]<f[1][0])
simil = filesPairs.map(similPair)
simil.saveAsTextFile('/user/pascepet/data/pismena/similarities.txt')


### Priklad 3: nasobeni matic

# vstupni data: ridke matice, 1 radek = 1 nenulovy prvek
# format radku: index radku, index sloupce, hodnota prvku

### konstanta - pocet radku a sloupcu matic
N = 10000

### cteni dat
matA = sc.textFile("/user/pascepet/data/matice/matice_a2.txt")
matB = sc.textFile("/user/pascepet/data/matice/matice_b2.txt")
# rozdeleni radku na indexy a hodnotu
matA = matA.map(lambda el: el.split(','))
matB = matB.map(lambda el: el.split(','))

# pokus (A)
# transformace - prvku se priradi vsechny vysledne prvky, do nichz muze prispivat; soucasti klice je i poradi scitance v souctu soucinu
# prvek leve matice se souradnicemi (i, j) prispiva do vsech prvku (i, k), kde k=1:N, a to do j-teho scitance
matA = matA.flatMap(lambda el: [((int(el[0]), j, int(el[1])), (float(el[2]), 1)) for j in range(1, N+1)])
# prvek prave matice se souradnicemi (i, j) prispiva do vsech prvku (k, j), kde k=1:N, a to do i-teho scitance
matB = matB.flatMap(lambda el: [((j, int(el[1]), int(el[0])), (float(el[2]), 1)) for j in range(1, N+1)])
mat = matA.union(matB) # spojeni do jednoho RDD

### shromazdi se prvky se stejnym klicem - tj. stejne scitance
# vynasobi se; nasobeni ale funguje i v pripade, kdy je jen jeden prvek (a druhy je nulovy), proto se zjisti i pocet nasobitelu
souciny = mat.reduceByKey(lambda a,b: (a[0]*b[0], a[1]+b[1]))
souciny = souciny.filter(lambda el: el[1][1]==2) # ponechaji se jen souciny, ktere jsou ze dvou prvku 

### seskupi se vsechny souciny vytvarejici stejny prvek, a ty se sectou
souciny = souciny.map(lambda el: ((el[0][0], el[0][1]), el[1][0]))
res = souciny.reduceByKey(lambda a,b: a+b).sortByKey()

# pokus (B)
# transformace - prvku se jako klic priradi poradi scitance a jako hodnota identifikace matice, index radku/sloupce a hodnota
matA = matA.map(lambda el: (int(el[1]), ('A', int(el[0]), float(el[2]))))
matB = matB.map(lambda el: (int(el[0]), ('B', int(el[1]), float(el[2]))))
# seskupi se prvky, ktere prispivaji do scitance se stejnym poradim, a udelaji se vsechny mozne dvojice
mat = matA.join(matB)
# transformace: z dvojic se vytahnou indexy jako novy klic a soucin hodnot prvku jako nova hodnota
souciny = mat.map(lambda pair: ((pair[1][0][1], pair[1][1][1]), pair[1][0][2]*pair[1][1][2]))
# souciny prvku se pronasobi
res = souciny.reduceByKey(lambda a,b: a+b)
res = res.sortByKey()
# vysledek
res.take(10)