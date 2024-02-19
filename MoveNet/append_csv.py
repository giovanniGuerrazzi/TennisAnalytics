import sys
import csv
import pandas as pd

"""

Script usato per unire due dataset (due file.csv): appende i file.csv (importante specificare window!)

"""

if len(sys.argv) != 4:
    print('run as: "python append_csv.py <file_da_appendere.csv> <file_dove_si_vuole_appendere.csv> <window>"')
    exit(1)

file_in = sys.argv[1]
file_out = sys.argv[2]
window = int(sys.argv[3])

if window % 5 != 0:
    exit()

# variabile che se vale 1 significa che il file di output dove si vanno ad appendere le righe è vuoto
empty = 1

# Default value is header=0 , which means the first row of the CSV file will be treated as column names.
# Uguale a scrivere: first = pd.read_csv(file_in1, header=0)
file_csv_in = pd.read_csv(file_in)  

# apro il file di output in lettura per vedere se è vuoto o meno 
with open(file_out, 'r') as file_csv_out:
    for row in file_csv_out:
        if row:
            # Se almeno una riga è presente, il file non è vuoto
            print('<file_dove_si_vuole_appendere> non vuoto')
            empty = 0
            break

if empty:
    """creazione riga iniziale che sara di questo tipo: (dove Y_i_j significa coordinata Y del frame i keypoint j)
    Y_0_0 X_0_0 ... Y_0_16 X_0_16 Y_1_0 X_1_0 ... Y_1_16 X_1_16 ... Y_10_16 X_10_16 Shot
    questo se window == 5
    per un totale di [2 x 17 x ((window * 2) + 1)] + 1 =  (con window == 5) 375 colonne (features)"""
    features = []
    for i in range(0, window*2 + 1):
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

    # Scrivo sul file di output l'header (visto che risulta essere vuoto)
    with open(file_out, 'w+') as file_csv_out:
        writer = csv.writer(file_csv_out, lineterminator='\n')
        # Esegui operazioni di scrittura qui
        writer.writerow(features)
        print('header scritto')

# file di output non più vuoto (o non lo è mai stato)

# Pandas DataFrame to CSV with no index can be done by using index=False param of to_csv() method. With this, you can
# specify ignore index while writing/exporting DataFrame to CSV file."""
# file_csv.to_csv(file_out, index=False)

# mode='a' significa che il file è aperto in scrittura modalità append
# mode='a+' significa che il file è aperto in lettura e scrittura modalità append
# header=False significa che la prima riga non la conto(come nome di ogni colonna)
file_csv_in.to_csv(file_out, index=False, header=False, mode='a')