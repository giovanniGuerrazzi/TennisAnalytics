import csv
import sys
import getopt

"""

Script che dato un file.csv come input (start_dataset.csv) restituisce un file avente come righe SOLO INTORNI di frame 
nei quale avviene un colpo (diritto o rovescio) con numero frame in cui avvienne il colpo. [In questo caso il file.csv di output
non contiene le colonne che corrispondono alla confidence score (s_)]
Parametri:
    - window: di default 5
    se avviene un colpo al frame 100 si prenderà come window un intorno di 5 frame (5 prima di 100 e 5 dopo) ovvero:
    ||95-99 frame prima del colpo || 100 frame COLPO || 101-105 frame dopo il colpo || per un totale di 11 frame (2 * windows + 1)

"""

# valori di default
# window = 5

try:
    (opts, args) = getopt.getopt(sys.argv[1:], '', [
        'input=',
        'output=',
        'window=',
    ])
    if len(opts) != 3:
        raise ''
except:
    print(' usage: python framing_without_s.py --input=<filecsvPath> --output=<outputPath> '
          ' --window=<window> ')
    exit(1)

# parsing dei dati passati da terminale come input
for (opt, arg) in opts:
    if opt == '--input':
        input = arg
    elif opt == '--output':
        output = arg
    elif opt == '--window':
        window = int(arg)
    else:
        print(
            ' usage: python framing_without_s.py --input=<filecsvPath> --output=<outputPath> '
            ' --window=<window> ')
        exit(1)

"""creazione riga iniziale che sara di questo tipo: (dove Y_i_j significa coordinata Y del frame i keypoint j)
S_Row Y_0_0 X_0_0 ... Y_0_16 X_0_16 Y_1_0 X_1_0 ... Y_1_16 X_1_16 ... Y_10_16 X_10_16 Shot
questo se window == 5
per un totale di 1 + [2 x 17 x ((window * 2) + 1)] + 1 = (con window == 5) 376 colonne (features)"""
features = []
features.append('S_Row')
for i in range(0, window * 2 + 1):
    # feature frame centrale
    if i == window:
        for j in range(0, 17):
            features.append('Y_SHOT_' + str(i) + '_' + str(j))
            features.append('X_SHOT_' + str(i) + '_' + str(j))
    else:
        for j in range(0, 17):
            features.append('Y_' + str(i) + '_' + str(j))
            features.append('X_' + str(i) + '_' + str(j))
features.append('Shot')

with open(input, 'r') as csvinput:
    with open(output, 'w+') as csvoutput:
        # ottengo gli oggetti di riferimento al file di input e output
        writer = csv.writer(csvoutput, lineterminator='\n')
        reader = csv.reader(csvinput)
        # scrivo l'header
        writer.writerow(features)
        # leggo la prima riga del file di input (l'header)
        row = next(reader)

        # inizializzo le varie varibili
        # columns_to_delete = [2,5,8,11,14,17,20,23,26,29,32,35,38,41,44,47,50]
        columns_to_remaining = [0,1,3,4,6,7,9,10,12,13,15,16,18,19,21,22,24,25,27,28,30,31,33,34,36,37,39,40,42,43,45,46,48,49]

        pre_frame   = []
        shot_frame  = []
        post_frame  = []
        final_row   = []
        value_shot = 0
        shot = 0
        cont = 0
        num_shots = 0

        # carico le prime <window> righe
        for _ in range(window):
            row = next(reader)
            # rimuovo il primo, l'ultimo elemento e le colonne che contengono la confidence score
            row.pop(0)
            row.pop()
            new_row = [row[i] for i in columns_to_remaining]
            pre_frame.append(new_row)
        # writer.writerow(val for list in pre_frame for val in list) 

        # scorro il resto del file di input andando alla ricerca dei frame caratterizzati da un colpo
        for row in reader:
            # è stato riscontrato uno shot, si prende l'intorno dei frame successivi
            if shot == 1:
                # si accumulano i frame successivi al frame dove è avvenuto lo shot
                if cont < window:
                    # da ciascuna riga rimuovo la prima e l'ultima colonna che contengono il numero del frame e 1/2 (shot)
                    row.pop(0)
                    row.pop()
                    # viene creata la nuova riga senza confidence_score
                    new_row = [row[i] for i in columns_to_remaining]
                    post_frame.append(new_row)
                    cont = cont + 1
                    continue
                # ora che abbiamo anche l'intorno successivo al colpo si scrive nel nuovo file la riga risultante
                else:
                    # list comprehension: creo la riga contenente i frame prima durante e dopo il colpo
                    final_row = final_row + [elem for elem in pre_frame]
                    final_row = final_row + [elem for elem in shot_frame]
                    final_row = final_row + [elem for elem in post_frame]
                    final_row = final_row + [[value_shot]]
                    final_row.insert(0, [s_row])
                    """Si esegue un ciclo su ogni elemento <list> in <final_row> e poi su ogni <val> in ogni <list>, 
                    scrivendo ciascun <val> come una colonna nel file.csv"""
                    # writer.writerow(val for list in final_row for val in list)
                    writer.writerow([val for list in final_row for val in list])
        
                    # aggiorno il pre_frame che diventerà il post_frame
                    pre_frame = post_frame
                    # vengono resettate le altre variabili
                    shot_frame = []
                    post_frame = []
                    final_row = []
                    shot = 0
                    cont = 0
                    # da ciascuna riga rimuovo la prima e l'ultima colonna che contengono il numero del frame e 0 (no shot)
                    row.pop(0)
                    row.pop()
                    # viene creata la nuova riga senza confidence_score
                    new_row = [row[i] for i in columns_to_remaining]
                    # aggiorno l'intorno precedente allo shot (di lunghezza window)
                    pre_frame.pop(0)
                    pre_frame.append(new_row)
            # siamo in presenza di uno shot
            elif int(row[52]) == 1 or int(row[52]) == 2:
                shot = 1
                value_shot = int(row[52])
                # si memorizza il numero di riga in cui avviene il colpo
                s_row = row[0]
                num_shots += 1
                # dalla riga rimuovo la prima e l'ultima colonna che contengono il numero del frame e 1/2 (shot)
                row.pop(0)
                row.pop()
                # viene creata la nuova riga senza confidence_score
                new_row = [row[i] for i in columns_to_remaining]
                shot_frame.append(new_row)
            # non siamo in presenza di uno shot
            else:
                # dalla nuova riga letta rimuovo la prima e l'ultima colonna che contengono il numero del frame e 0 (no shot)
                row.pop(0)
                row.pop()
                # viene creata la nuova riga senza confidence_score
                new_row = [row[i] for i in columns_to_remaining]
                # aggiorno l'intorno precedente allo shot (di lunghezza window)
                pre_frame.pop(0)
                pre_frame.append(new_row)

print(f'numero di colpi registrati:{num_shots}')
        