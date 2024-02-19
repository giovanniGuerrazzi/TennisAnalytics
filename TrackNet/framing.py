import csv
import sys
import getopt

"""

Script che dato un file.csv come input (start_dataset.csv) restituisce un file avente come righe SOLO INTORNI di frame 
nei quale avviene un colpo (diritto o rovescio).
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
    print(' usage: python framing.py --input=<filecsvPath> --output=<outputPath> '
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
            ' usage: python framing.py --input=<filecsvPath> --output=<outputPath> '
            ' --window=<window> ')
        exit(1)

"""creazione riga iniziale che sara di questo tipo:
S_Row Vis_0 X_0 Y_0 .... Vis_4 X_4 Y_4 Vis_Shot X_Shot_5 Y_shot_5 Vis_6 X_6 Y_6 ... Vis_10 X_10 Y_10 Shot
questo se window == 5
per un totale di 1 + [3 * ((window * 2) + 1)] + 1 =  34 colonne (features) nel caso di window = 5"""
features = []
features.append('S_Row')
for i in range(0, window * 2 + 1):
    # feature frame centrale
    if i == window:
        features.append('Vis_Shot_' + str(i))
        features.append('X_Shot_' + str(i))
        features.append('Y_Shot_' + str(i))
    else:
        features.append('Vis_' + str(i))
        features.append('X_' + str(i))
        features.append('Y_' + str(i))
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
            # rimuovo il primo, l'ultimo e il penultimo elemento (il numero del frame,la colonna dello shot e time)
            row.pop(0)
            row.pop()
            pre_frame.append(row)
    
        # scorro il resto del file di input andando alla ricerca dei frame caratterizzati da un colpo
        for row in reader:
            # si controlla se è stato riscontrato uno shot, si prende l'intorno dei frame successivi
            if shot == 1:
                # si accumulano i frame successivi al frame dove è avvenuto lo shot
                if cont < window:
                    # da ciascuna riga rimuovo il primo, l'ultimo e il penultimo elemento (il numero del frame,la colonna dello shot e time)
                    row.pop(0)
                    row.pop()
                    post_frame.append(row)
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
                    # da ciascuna riga rimuovo il primo, l'ultimo e il penultimo elemento (il numero del frame,la colonna dello shot e time)
                    row.pop(0)
                    row.pop()
                    # aggiorno l'intorno precedente allo shot (di lunghezza window)
                    pre_frame.pop(0)
                    pre_frame.append(row)
            # si controlla se siamo in presenza di uno shot
            elif int(row[4]) == 1 or int(row[4]) == 2:
                shot = 1
                value_shot = int(row[4])
                # si memorizza il numero di riga in cui avviene il colpo
                s_row = row[0]
                num_shots += 1
                # dalla riga rimuovo il primo, l'ultimo e il penultimo elemento (il numero del frame, la colonna dello shot e time)
                row.pop(0)
                row.pop()
                shot_frame.append(row)
            # altrimenti non siamo in presenza di uno shot
            else:
                # dalla riga rimuovo il primo, l'ultimo e il penultimo elemento (il numero del frame, la colonna dello shot e time)
                row.pop(0)
                row.pop()
                # aggiorno l'intorno precedente allo shot (di lunghezza window)
                pre_frame.pop(0)
                pre_frame.append(row)

print(f'numero di colpi registrati:{num_shots}')
        