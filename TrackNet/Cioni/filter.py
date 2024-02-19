import csv
import sys

""" 

Script che prende il csv e lo filtra, bisogna passare la lunghezza della sequenza (15 frame nel nostro caso, 5-5-5) e di quanto
vogliamo filtrare ogni finestra (es: 2 elimina ogni riga che non ha almeno 2 frame prima 2 dentro e 2 dopo quella centrale)

"""

if len(sys.argv) != 5:
    print('run as: "python filter.py <file.csv> <output.csv> <window> <filter>"')
    exit(1)

# valori che usiamo
# window = 15 o 9
# filter = 1 e 2
    
input = sys.argv[1]
output = sys.argv[2]
window = int(sys.argv[3])
filter = int(sys.argv[4])
all = []

with open(input,'r') as inp, open(output,'w+') as out:

    # apertura nuovo file in scrittura (file che risulterà filtrato)
    writer = csv.writer(out,lineterminator='\n')
    # apertura in lettura del file da filtrare
    reader = csv.reader(inp)

    # viene costruito l'header del file (47 colonne = 15 * 3 + 1 (frame/riga) + 1 (shot))
    # Row, Vis0, X0, Y0, ..., Vis14, X14, Y14, 'Shot'
    header = []
    header.append('Row')
    for i in range(0, window):
        header.append('Vis' + str(i))
        header.append('X' + str(i))
        header.append('Y' + str(i))
    header.append('Shot')
    # print(header)

    # si scrive l'header nel file di output
    writer.writerow(header)

    # si legge l'header nel file di input
    row = next(reader)

    for row in reader:
        # inizializzazione variabili
        pre = 0
        inside = 0
        after = 0
        # VIENE SALTATA LA PRIMA RIGA PERCHE' CONTIENE IL NUMERO DI RIGA E L'ULTIMA COLONNA IN QUANTO CONTIENE LO 'SHOT'
        # si controlla se nei 5 frame (15 colonne) prima del colpo c'è almeno 1/2 frame dove la pallina viene tracciata
        for tmp in row[1:window + 1]:
            if tmp == '1':
                pre = pre + 1
        # si controlla se nei 5 frame (15 colonne) centrali c'è almeno 1/2 frame dove la pallina viene tracciata
        for tmp in row[window + 1:window * 2 + 1]:
            if tmp == '1':
                inside = inside + 1
         # si controlla se nei 5 frame (15 colonne) dopo il colpo c'è almeno 1/2 frame dove la pallina viene tracciata
        for tmp in row[window * 2 + 1:window * 3 + 1]:
            if tmp == '1':
                after = after + 1
        if pre >= filter and inside >= filter and after >= filter:
            all.append(row)
            # print(row)
        
    writer.writerows(all)
    
