import csv
import sys
import json

"""

Script che prende come input un file.json (ottenuto analizzando frame by frame il video.mp4 tramite Label-Studio)
e un file.csv ottenuto tramite MoveNet e restituisce un nuovo file.csv dove è presente  una colonna finale 'Shot' contenente
uno frai seguenti valori a seconda se c'è stato un colpo o meno:

 - 0 nessun colpo 
 - 1 diritto 
 - 2 rovescio 
 
 """


if len(sys.argv) != 4:
    print('run as: "python csv_read.py <file.json> <input.csv> <output.csv> "')
    exit(1)

jsonfile = sys.argv[1]
input = sys.argv[2]
output = sys.argv[3]

# apro il json e mi salvo i frame in un array
f = open(jsonfile)
data = json.load(f)

diritti = []
rovesci = []

# numero di frame etichettati
num_frames_labeled = len(data[0]['box'])
print(num_frames_labeled)
# si itera per ogni frame etichettato come colpo (grazie al file.json)
for k in range(0, num_frames_labeled):
    if len(data[0]['box'][k]['sequence']) != 0:
        # frame etichettato come diritto
        if data[0]['box'][k]['labels'][0] == 'Diritto':
            diritti.append(data[0]['box'][k]['sequence'][0]['frame'])
        # frame etichettato come rovescio
        elif data[0]['box'][k]['labels'][0] == 'Rovescio':
            rovesci.append(data[0]['box'][k]['sequence'][0]['frame'])

# creo il nuovo file.csv con l'aggiunta della colonna 'Hit'
with open(input, 'r') as csvinput:
    with open(output, 'w+') as csvoutput:
        writer = csv.writer(csvoutput, lineterminator='\n')
        reader = csv.reader(csvinput)
        
        # creo la prima riga del nuovo file.csv che sarà così: ['Frame', 'Y_0', 'X_0', 'S_0', ..., 'Y_16', 'X_16', 'S_16', 'Shot']
        row = next(reader)
        row.append('Shot')
        writer.writerow(row)

        # successivamente viene aggiunta la nuova colonna con il valore corrispondente allo 'Hit' per ogni riga
        for row in reader:
            if int(row[0]) in diritti:
                row.append('1')
            elif int(row[0]) in rovesci:
                row.append('2')
            else:
                row.append('0')
            writer.writerow(row)

# si stampano dati utili
print('diritti')
print(diritti)
print(len(diritti))

print('rovesci')
print(rovesci)
print(len(rovesci))

f.close()


