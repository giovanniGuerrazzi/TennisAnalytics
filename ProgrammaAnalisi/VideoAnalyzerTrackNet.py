import joblib
import sys
import csv
import subprocess
import pandas as pd

"""

Questo script permette di analizzare un video di tennis dove i colpi ci vengono forniti dal file csv in input ottenuto 
dal modello Cioni restituendo come output un video dove la tipologia di colpo "diritto-rovescio" è segnata a video

"""

print("Pre Fase 0: Lettura dati di input")
# passo 0) -----------------------------------------------------------------
# lettura dati di input
if(len(sys.argv) != 4):
    print('run as: "python VideoAnalyzerTrackNet.py <video_da_analizzare> <file_csv_TrackNet_con_colpi_Cioni> <file_csv_TrackNet_base_senza_colpi>')
    exit(1)

video = sys.argv[1]
tracknet_csv = sys.argv[2]
tracknetbase_csv = sys.argv[3]
print("Post Fase 0")

print("Pre Fase 1: Normalizzazione coordinate x e y pallina")
# passo 1)  -----------------------------------------------------------------
# normalizzazione delle coordinate della pallina reperita tramite TrackNet
arguments = [tracknetbase_csv, './FINAL_DATA/fileTrackNet/tracknet_norm.csv']
subprocess.call(['python','./normTRACK.py'] + arguments)
print("Post Fase 1")

print("Pre Fase 2: Caricamento modello di Machine Learning allenato")
# passo 2)  -----------------------------------------------------------------
# si carica il modello allenato
RF = joblib.load('./FINAL_DATA/models/RF.joblib')
print("Post Fase 2")

print("Pre Fase 3: Creazione nuovo dataset con colonna aggiuntiva 'Shot'")
# passo 3)  -----------------------------------------------------------------
# viene creato il nuovo dataset contenente una colonna finale aggiuntiva 'Shot' che ci dice se in quel frame c'è 
# stato un colpo o meno (questo dataset ci viene fornito grazie al modello Cioni). Nessuna informazione sul tipo di colpo
with open(tracknet_csv,'r') as input:
    reader = csv.reader(input)
 
    # variabile che conterrà tutte le righe contenenti colpi
    shots = []
    # contatore numero di riga file in lettura
    num_row = 0
    # variabile che ci permette di contare solo un frame come colpo e non 5 (visto che dal file tracknet di Cioni ne ha contati 5)
    colp_count = 0

    # lettura header 
    header = next(reader)

    for row in reader:

        if row[3] == '2':
            colp_count += 1
            if colp_count == 3:
                shots.append(num_row)
            if colp_count == 5:
                colp_count = 0
      
        # avanzamento contatore riga   
        num_row += 1


with open("./FINAL_DATA/fileTrackNet/tracknet_norm.csv", 'r') as input:
    with open("./FINAL_DATA/fileTrackNet/tracknet_norm_with_shots.csv", 'w+', newline='') as output:
        reader = csv.reader(input)
        writer = csv.writer(output,lineterminator='\n')

        # lettura dell'header
        row = next(reader)

        # creazione file csv conntenente i colpi etichettati solamente come '1'
        header = ['Frame', 'Vis', 'X', 'Y', 'Shot']
      
        writer.writerow(header)

        # successivamente viene aggiunta la nuova colonna con il valore corrispondente allo 'Shot' per ogni riga
        for row in reader:
            if int(row[0]) in shots:
                row.append('1')
            else:
                row.append('0')
            writer.writerow(row)

print("Post Fase 3")

print("Pre Fase 4: Creazione dataset intorno colpi")
# passo 4)  -----------------------------------------------------------------
# creazione dataset avente solamente intorni di colpi
arguments = ['--input=./FINAL_DATA/fileTrackNet/tracknet_norm_with_shots.csv', '--output=./FINAL_DATA/fileTrackNet/tracknet_norm_only_shots.csv', '--window=5']
subprocess.call(['python','./framing.py'] + arguments)
print("Post Fase 4")

print("Pre Fase 5: Fase di predizione tramite il modello")
# passo 5)  -----------------------------------------------------------------
# utilizzo modello allenato 
# lettura del dataset e memorizzazione in un DataFrame: header=0 indica che la prima riga del file CSV contiene i nomi delle colonne
dataset = pd.read_csv('./FINAL_DATA/fileTrackNet/tracknet_norm_only_shots.csv', sep=',', header=0)

# Anteprima dataset
print(dataset.head())

# Numero di colonne - 1 perchè si parte da 0 (non si conta la colonna finale 'Shot')
index_last_column = len(dataset.columns) - 1

# Vengono prese tutte le righe e tutte le colonne a eccezione della prima (S_Row) [FONDAMENTALE] e dell'ultima ('Shot') quindi abbiamo una matrice n x m-2
# X sono i campioni!
X = dataset.iloc[:, 1:index_last_column]
# colonna che contiene il numero di frame dove avviene il colpo
colonna_shots_true = dataset.iloc[:,0]

# si converte in lista visto che è un Serie pandas
col_shots_true_list = colonna_shots_true.tolist()

# si effettuano le predizioni con il modello allenato
prediction = RF.predict(X)

print(prediction)

# si controlla quanti colpi sono stati etichettati come diritti e quanti come rovesci
diritti = 0
rovesci = 0
for shot in prediction:
    if shot == 1:
        diritti += 1
    if shot == 2:
        rovesci += 1
print(f'numero di diritti riscontrati:{diritti}')
print(f'numero di rovesci riscontrati:{rovesci}')
print(len(prediction))
print("Post Fase 5")

print("Pre Fase 6: Ricostruzione file originario con tipologia colpi predetta")
# passo 6)  -----------------------------------------------------------------
# ricostruzione del file originario con la tipologia dei colpi predetti
# with open("./FINAL_DATA/fileTrackNet/tracknet_norm_with_shots.csv", 'r') as input:
with open("./FINAL_DATA/fileTrackNet/tracknet_norm.csv", 'r') as input:
    with open("./FINAL_DATA/fileTrackNet/tracknet_norm_with_shots_predict.csv", 'w+', newline='') as output:
        reader = csv.reader(input)
        writer = csv.writer(output,lineterminator='\n')

        # lettura dell'header
        row = next(reader)

        # creazione file csv con i dati normalizzati di TrackNet, come prima cosa si crea l'header del nuovo file
        header = ['Frame', 'Vis', 'X', 'Y', 'Shot']
        # scrittura header
        writer.writerow(header)

        # contratore che ci serve per scrorrere i valore predetti nonchè i frame dove ci sono i colpi
        cont = 0
        # successivamente viene aggiunta la nuova colonna con il valore corrispondente allo 'Shot' per ogni riga
        for row in reader:
            # controllo che l'indice non superi l'upper bound
            if cont < len(prediction):
                # frame dove avviene il colpo
                if int(row[0]) in col_shots_true_list:
                    row.append(prediction[cont])
                    cont += 1
                    writer.writerow(row)
                # frame dove non avviene il colpo
                else:
                    row.append('0')
                    writer.writerow(row)
            # per finire di scrivere le righe una volta che sono stati scritti tutti i frame predetti
            else:
                row.append('0')
                writer.writerow(row)

print("Post Fase 6")

print("Pre Fase 7: Analisi video")
# passo 7)  -----------------------------------------------------------------
# creazione del nuovo video con i predict a video
arguments = [video, './FINAL_DATA/fileTrackNet/tracknet_norm_with_shots_predict.csv', './FINAL_DATA/video/non_perf/tracknet/video_tennis_predict_perfect_11.mp4']
print('sta venendo analizzato il video attendere circa 2/3 minuti...')
subprocess.call(['python','./VideoPrinter.py'] + arguments)
print('video analizzato!')
print("Post Fase 7")

print("Finished")
