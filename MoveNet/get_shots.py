import csv
import sys

"""

Script che prende come input un file.csv e restituisce come output un file.csv che contiene solo i frame caratterizzati 
da un colpo (diritto o rovescio). In particolare: Shot = 1 -> diritto, Shot = 2 -> rovescio  e lo stampa a schermo
 
"""

if len(sys.argv) != 3:
    print('run as: "python get_shots.py <input.csv> <output.csv> "')
    exit(1)

input = sys.argv[1]
output = sys.argv[2]
cont = 0

# creo il file.csv di output contenente solo colpi leggendo il file di input e scrivendo nel nuovo file.csv
with open(input, 'r') as csvinput:
    with open(output, 'w+') as csvoutput:
        # ottengo i gli oggetti di riferimento al file di input e output
        writer = csv.writer(csvoutput, lineterminator='\n')
        reader = csv.reader(csvinput)
        # leggo e scrivo la prima riga inerente al nome delle varie colonne
        row = next(reader)
        writer.writerow(row)

        # leggo e scrivo le righe che contengono come colonna finale il valore 1 o 2
        for row in reader:
            if int(row[52]) == 1 or int(row[52]) == 2:
                cont = cont + 1
                writer.writerow(row)

        print(f' Numero di shot presenti:{cont}')