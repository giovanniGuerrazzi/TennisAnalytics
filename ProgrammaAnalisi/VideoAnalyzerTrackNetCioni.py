import joblib
import sys
import csv
import subprocess
import pandas as pd

"""

Questo script permette di ottenere un file csv contenente i colpi predetti dal modello allenato da Cioni prendendo come input
un video in formato mp4 assieme alle sue risoluzioni.

"""

print("Pre Fase 0: Lettura dati di input")
# passo 0) -----------------------------------------------------------------
# lettura dati di input
if(len(sys.argv) < 5):
    print('run as: "python VideoAnalyzerTrackNetCioni.py <video_da_analizzare> <tracknet_dataset.csv> <x_res> <y_res>"')
    exit(1)

# dati di input, con window e interval
video = sys.argv[1]
# questo file sarà caratterizzato dalle seguenti colonne: Frame, Vis, X, Y, Time (NO SHOT! va ricavato)
tracknetcsv = sys.argv[2]
window = 15
interval = 5
xres = int(sys.argv[3])
yres = int(sys.argv[4])
print("Post Fase 0")

print("Pre Fase 0.5: Caricamento modello di Machine Learning allenato da Cioni")
# passo 0.5) -----------------------------------------------------------------
# si carica il modello allenato su precedenti video (allenato da Cioni con scikit-learn 1.2.2)
RF = joblib.load('./FINAL_DATA/models/RF_Cioni.joblib')
print("Post Fase 0.5")

print("Pre Fase 1: Creazione dataset 5-5-5 con colonna 'Shot'")
# passo 1) -----------------------------------------------------------------
# viene creato il primo dataset, quello con 15 * 3 colonne + 1 (numero di riga) (5-5-5)


# viene costruito l'header del file (47 colonne = 15 * 3 + 1 (frame/riga) + 1 (shot))
# Row, Vis0, X0, Y0, ..., Vis14, X14, Y14, 'Shot'
field = []
field.append('Row')
for i in range(0, window):
    field.append('Vis' + str(i))
    field.append('X' + str(i))
    field.append('Y' + str(i))
field.append('Shot')

# variabile che serve per costruire la riga del nuovo file che conterrà 15 frame consecutivi (5-5-5)
tmp = []
# variabile che serve per tenere di conto a che iterazione siamo
iter = 0
# variabile che serve per tenere di conto del numero di righe! (frame)
riga = 1

with open(tracknetcsv,'r') as csvinput:
    # dataset restituito in output avente 47 colonne (nuovo file)
    with open("./FINAL_DATA/fileTrackNet/tracknet_new_dataset.csv", 'w+') as csvoutput:
        # si ottengono i corrispettivi puntatori in lettura e scrittura
        reader = csv.reader(csvinput)
        writer = csv.writer(csvoutput,lineterminator='\n')

        # si scrive l'header nel file di output
        writer.writerow(field)
        # viene letta la prima riga dal file.csv d'input (quella che contiene i nomi dei campi)
        row = next(reader)

        # quello che viene fatto in new_csv_read.py (creazione file 5-5-5 per riga)
        while(True):
            try:
                # a ogni iterazione del ciclo vengono SALTATE <iter> * <interval> righe
                for k in range(0, iter * interval + 1):
                    # viene portato avanti il puntatore del file (verrà resettato ogni volta vedi dopo)
                    row = next(reader)
                # si inizializza il valore dei colpi a 0 per tutte le righe!!!! (colonna 'Shot' di questo dataset sarà full di 0)
                shot = '0'
                
                # si inserisce il numero di riga
                tmp.append(riga)

                # si normalizzano le coordinate x e y della pallina tracciata in 15 righe (window)
                # LETTURA delle righe da mettere insieme in modo tale da formare la struttura 5-5-5
                for i in range(0, window):
                    row = next(reader)
                    # si salta row[0] in quanto è il numero di frame
                    # si appende la Vis
                    tmp.append(row[1])
                    # si appendono le coordinate normalizzate
                    x = round((int(row[2]) / xres) * 100, 3)
                    tmp.append(str(x))
                    y = round((int(row[3]) / yres) * 100, 3)
                    tmp.append(str(y))

                # nella riga NON HO l'informazione inerente al colpo, me la devo ricavare dal modello allenato.
                # Quindi per ora si mette di default a 0
                tmp.append(shot)
                # scrittura della nuova riga contenente la colonna 'Shot'
                writer.writerow(tmp)

                # si svuota tmp e si aggiorna il numero di riga e iterazioni
                tmp = []
                riga += 1
                iter = iter + 1
                # viene ricollocato il puntatore di lettura a inizio file (reset puntatore)
                csvinput.seek(0)

            except Exception as e:
                print(e)
                break
print("Post Fase 1")

print("Pre Fase 2: Filtraggio dataset")
# passo 2) -----------------------------------------------------------------
# filtraggio dataset 5-5-5 contenente almeno 1 frame per ogni intorno di 5
arguments = ['./FINAL_DATA/fileTrackNet/tracknet_new_dataset.csv', './FINAL_DATA/fileTrackNet/tracknet_new_dataset_filter.csv', '15', '1']
subprocess.call(['python','./filter.py'] + arguments)
print("Post Fase 2")

print("Pre Fase 3: Creazione dataset con differenze tra primo e ultimo frame")
# passo 3) -----------------------------------------------------------------
# creazione dataset con differenze
arguments = ['./FINAL_DATA/fileTrackNet/tracknet_new_dataset_filter.csv', './FINAL_DATA/fileTrackNet/tracknet_new_dataset_filter_difference.csv', '15', '5','9']
subprocess.call(['python','./difference_xy.py'] + arguments)
print("Post Fase 3")

print("Pre Fase 4: Utilizzo del modello allenato per il riconoscimento di colpi")
# passo 4) -----------------------------------------------------------------
# utilizzo modello allenato 
# lettura del dataset e memorizzazione in un DataFrame: header=0 indica che la prima riga del file CSV contiene i nomi delle colonne
dataset = pd.read_csv('./FINAL_DATA/fileTrackNet/tracknet_new_dataset_filter_difference.csv', sep=',', header=0)

# Anteprima dataset
print(dataset.head())
print('\n')

# Numero di colonne - 1 perchè si parte da 0 (non si conta la colonna finale 'Shot')
index_last_column = len(dataset.columns) - 1

# Vengono prese tutte le righe e tutte le colonne a eccezione della prima (numero di riga) e dell'ultima ('Shot') quindi abbiamo una matrice n x m-2
# X sono i campioni!
X = dataset.iloc[:, 1:index_last_column]

print(X)

# si effettuano le predizioni con il modello allenato
prediction = RF.predict(X)

# tutte le predizioni per i frame accorpati e filtrati e diffati con media
print(prediction)

# si prendono tutte le righe (prima colonna) del dataset filtrato (5-5-5) a cui è stata calcolata la diff e media
column_array = dataset.iloc[:, 0]
rows = column_array.values

# si contano i numero di COLPI predictati
num_shot_predicted = 0
for i in prediction:
    if i == 2:
        num_shot_predicted += 1
print(f'numero di colpi predictati:{num_shot_predicted}')
print("Post Fase 4")

print("Pre Fase 5: ricostruzione dataset originale con aggiunta colpi predetti")
# passo 5) -----------------------------------------------------------------
# costruzione file output del tipo 5-5-5 con colonna 'Shot' aggiornata con i valori predetti
with open('./FINAL_DATA/fileTrackNet/tracknet_new_dataset.csv', 'r') as csvinput:
    with open('./FINAL_DATA/fileTrackNet/tracknet_dataset_final.csv','w+') as csvoutput:
        reader = csv.reader(csvinput)
        writer = csv.writer(csvoutput,lineterminator='\n')
        # si legge l'header
        row = next(reader)
        # si scrive l'header
        writer.writerow(row)

        # contatore che andrà da 0 a len(rows)
        number = 0 

        for row in reader:
            # controllo che l'indice non superi l'upper bound
            if number < len(prediction):
                # rows è un vettore n x 1 contenente il numero di riga del dataset dato in pasto al modello per le previsioni
                # se le righe coincidono si aggiorna il valore 'Shot' con quello predetto per quel particolare frame
                if int(row[0]) == rows[number]:
                    # row[-1] per accedere all'ultimo campo nonchè 'Shot'
                    row[-1] = prediction[number]
                    number += 1
                writer.writerow(row)
            # per finire di scrivere le righe una volta che sono stati scritti tutti i frame predetti
            else:
                writer.writerow(row)
       

# ricreo il formato del dataset ORIGINALE di tracknet (senza time)  ovvero: ['Vis', 'X', 'Y', 'Shot'] con i predict del modello
with open('./FINAL_DATA/fileTrackNet/tracknet_dataset_final.csv', 'r') as csvinput:
    with open('./FINAL_DATA/fileTrackNet/colpi_fede/tracknet_dataset_predicted_11.csv','w+') as csvoutput:
        # si ottengono i puntatori del file in lettura e scrittura 
        reader = csv.reader(csvinput)
        writer = csv.writer(csvoutput,lineterminator='\n')
        # si legge l'header del file in input
        row = next(reader)
        # print(row)
        # creazione header finale
        labels = ['Vis', 'X', 'Y', 'Shot']
        # scrittura header 
        writer.writerow(labels)

        # variabile che ci permette di fare un'iterazione speciale una volta sola all'interno del while
        only_first_time = 0

        while(True):
            try:
                # serve solo per la prima iterazione!
                only_first_time += 1
                # lista che conterrà 5 o 10 (la primissima volta) nuove righe create:[[Vis, X, Y, Shot], ..., [Vis, X, Y, Shot]]
                # ogni volta a inizio while si azzera
                all = []
                # lista che conterrà la nuova riga creata: [Vis, X, Y, Shot], ogni volta a inizio while si azzera
                new_final_row = []
                # si legge la successiva riga
                row = next(reader)
                # si scrivono i PRIMISSIMI 10 frame quindi 30 colonne delle prime 45 (dato che ogni 3 colonne si fa una riga originale)
                if only_first_time == 1:
                    # si parte da 1 perchè l'indice 0 è l'indice di riga che non ci interessa
                    for i in range(1, 31):
                        # si scrivono i primi 5 (con le relative 3 info VIS,X,Y)
                        if 1 <= i <= 15:
                            if i % 3 == 0:
                                # si appende il campo Y
                                new_final_row.append(row[i])
                                # si appende il campo 'Shot' in quanto si trova dopo Y con '0' VISTO CHE SONO LE PRIME RIGHE
                                new_final_row.append('0')
                                # abbiamo ricostruito una riga originaria di tracknet con piu 'Shot'
                                all.append(new_final_row)
                                # si riazzera la nuova riga
                                new_final_row = []
                            # si appende o il campo VIS o X (row[i] con i = 1,2) !!!
                            else:
                                new_final_row.append(row[i])
                        # per 'i' che va praticamente da 16 a 30 (for) si scrivono i successivi 5 frame dopo i primi 5 (con le relative 3 info VIS,X,Y)
                        elif i > 15 :
                                if i % 3 == 0:
                                    # si appende il campo Y
                                    new_final_row.append(row[i])
                                    # si appende il campo 'Shot' vero (può essere anche 0)
                                    new_final_row.append(row[-1])
                                    # abbiamo ricostruito una riga originaria di tracknet con più 'Shot'
                                    all.append(new_final_row)
                                    # si riazzera la nuova riga
                                    new_final_row = []
                                else:
                                    # si appende o il campo VIS o X (row[i] con i = 1,2) !!!
                                    new_final_row.append(row[i])
                    # scrittura delle nuove righe sul file di output (da notare writerowS) 
                    # 5 contenenti i frame prima del colpo e 5 durante il colpo 
                    writer.writerows(all)
                # si scrivono tutti i frame rimanenti (nonchè tutti - 10 causa prima iterazione) prendendone 5 alla volta
                else:
                    # si scrivono i successivi 5 frame. FONDAMENTALE il range 16-31 che ci permette cosi poi di leggere 5 frame sempre
                    # nuovi dalle righe nuove evitando di leggere frame/righe gia lette!
                    for i in range(16, 31):
                        if(i % 3 == 0):
                            # si appende il campo Y
                            new_final_row.append(row[i])
                            # si appende il campo 'Shot' vero (può essere anche 0)
                            new_final_row.append(row[-1])
                            # abbiamo ricostruito una riga originaria di tracknet con più 'Shot'
                            all.append(new_final_row)
                            # si riazzera la nuova riga
                            new_final_row = []
                        else:
                            # si appende o il campo VIS o X (row[i] con i = 1,2) !!!
                            new_final_row.append(row[i])
                    # scrittura delle nuove righe sul file di output (da notare writerowS) 
                    writer.writerows(all)
            except Exception as e:
                print(e)
                break       
print("Post Fase 5")

print("Finished")
