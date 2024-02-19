import csv
import sys
import numpy as np
import math

"""

Script utilizzato per normalizzare le coordinate del giocatore rispetto all'altezza e al centro del corpo

"""


if len(sys.argv) != 3:
    print('run as: "python norm.py <movenet_base.csv> <movenet_norm.csv> "')
    exit(1)

input = sys.argv[1]
output = sys.argv[2]

with open(input, 'r') as csvinput:
    with open(output, 'w+') as csvoutput:
        reader = csv.reader(csvinput)
        writer = csv.writer(csvoutput, lineterminator='\n')

        # creazione file csv con i dati normalizzati di MoveNet, come prima cosa si crea l'header del nuovo file
        header_list = []
        header_list.append('Frame')
        for i in range(0,17):
            header_list.append('Y_' + str(i))
            header_list.append('X_' + str(i))
            header_list.append('S_' + str(i))

        writer.writerow(header_list)

        # si legge l'header del file aperto in lettura
        first_row = next(reader)
        # print(first_row)

        new_row = []
        key_points_norm = []
        num_frame = 0

        # si legge tutto il file
        for row in reader:

            # ogni riga contiene 52 colonne: la prima 'Frame' e le altre 51 = 17 x 3 sono le y,x,s feature del frame
            new_row.append(num_frame)
            num_frame += 1

            # spalla sx,spalla dx
            shoulders_mean_x = ((float(row[17]) + float(row[20])) / 2)
            shoulders_mean_y = ((float(row[16]) + float(row[19])) / 2)
            # fianco sx,fianco dx
            hips_mean_x = ((float(row[35]) + float(row[38])) / 2)
            hips_mean_y = ((float(row[34]) + float(row[37])) / 2)
            # si calcola l'altezza per quel frame
            height_top_x = shoulders_mean_x
            height_top_y = shoulders_mean_y
            height_bot_x = hips_mean_x
            height_bot_y = hips_mean_y
            # calcolo la norma dell'altezza
            vect_height_top = np.array([height_top_x, height_top_y])
            vect_height_bot = np.array([height_bot_x, height_bot_y])
            h = np.linalg.norm(vect_height_top - vect_height_bot, 2)
            # si normalizzano tutti i punti chiave rispetto all'altezza del giocatore
            for i in range (1,52): # va da 1 a 51 (51 iterazioni)
                if i % 3 != 0:
                    key_points_norm.append(float(row[i]) / h)
                else:
                    key_points_norm.append(float(row[i]))
      
            # spalla sx normalizzata,spalla dx normalizzata (indice -1 perchè key_points_norm parte subito da 0 non avendo il frame)
            neck_x = ((key_points_norm[16] + key_points_norm[19]) / 2)
            neck_y = ((key_points_norm[15] + key_points_norm[18]) / 2)

            # si normalizzano tutti i punti chiave rispetto al centro del giocatore (collo)
            for i in range(1, 52): # va da 1 a 51 (51 iterazioni)
                if i % 3 != 0: 
                    if i % 3 == 1: # y coordinate
                        val_y = key_points_norm[i - 1] - neck_y
                        new_row.append(round(val_y, 3))
                    if i % 3 == 2: # x coordinate
                        val_x = key_points_norm[i - 1] - neck_x
                        new_row.append(round(val_x, 3)) 
                else: # s score
                    new_row.append(row[i])   

            writer.writerow(new_row)

            new_row = []
            key_points_norm = []

              

