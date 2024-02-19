import csv
import sys

"""

Script che prende come input un file.csv e restituisce come output un file.csv che contiene solo i frame caratterizzati 
da un colpo (diritto o rovescio). In particolare: Shot = 1 -> diritto, Shot = 2 -> rovescio e lo stampa a schermo

"""

if len(sys.argv) != 2:
    print('run as: "python num_row_shots.py <file.csv>"')
    exit(1)

input = sys.argv[1]
cont = 0

# creo il file.csv di output contenente solo colpi leggendo il file di input e scrivendo nel nuovo file.csv
with open(input, 'r') as csvinput:
    # ottengo il riferimento al file di input
    reader = csv.reader(csvinput)
    # leggo e scrivo la prima riga inerente al nome delle varie colonne
    row = next(reader)

    # leggo e scrivo le righe che contengono come colonna finale il valore 1 o 2
    for row in reader:
        if int(row[3]) == 1 or int(row[3]) == 2:
            cont = cont + 1

    print(f' Numero di shot presenti:{cont}')