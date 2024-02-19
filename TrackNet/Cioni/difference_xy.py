import csv
import sys

"""

Script è stato creato appositamente per analizzare nuovi video dato che MANTIENE il numero della riga e quindi è necessario per
ricreare il dataset dopo l'analisi fatta dal modello e annotare il video.
Crea il dataset con la differenza fra il primo e l'ultimo frame delle finestre, in più calcola la media della finestra centrale

"""

# funzione che calcola la media e la diff nelle finestre di frame (5-5-5)
def first_last(ctrl, row, k, firstlast, avg=None):
    # significa che stiamo valutando il campo Vis del file csv quindi saltiamo questa feature
    if(ctrl == 0):
        return 
    # significa che stiamo valutando il campo X del file csv 
    elif(ctrl == 1):
        # controlliamo se X_i è != 0
        if(float(row[k]) != 0):
            # se la X1 è 0 aggiorno la nuova X1 (primo frame!)
            if(firstlast[0] == 0):
                firstlast[0] = float(row[k])
            # altrimenti la metto come X2 indipendentemente (voglio l'ultimo frame!)
            else:
                firstlast[1] = float(row[k])
            # media
            if(avg != None):
                avg[0] += float(row[k])
                avg[1] += 1
        return
    # significa che stiamo valutando il campo Y del file csv 
    else:
        # controlliamo se Y_i è != 0
        if(float(row[k])!= 0):
             # se la Y1 è 0 aggiorno la nuova Y1 (primo frame!)
            if(firstlast[2] == 0):
                firstlast[2] = float(row[k])
            # altrimenti la metto come Y2 indipendentemente (voglio l'ultimo frame!)
            else:
                firstlast[3] = float(row[k])
            # media
            if(avg != None):
                avg[2] += float(row[k])
                avg[3] += 1
        return

# main    
def main():
    if(len(sys.argv) != 6):
        print('run as: "python difference_xy.py <input.csv> <output.csv> <window> <shot_start> <shot_end>"')
        exit(1)

    # lettura dati di input
    input = sys.argv[1]
    output = sys.argv[2]
    window = int(sys.argv[3])
    shot_start = int(sys.argv[4])
    shot_end = int(sys.argv[5])

    # valori di default
    # window = 15
    # shot_start = 5
    # shot_end = 9

    # apertura dei file in lettura e scrittura
    with open(input,'r') as csvinput:
        with open(output, 'w+') as csvoutput:
            reader = csv.reader(csvinput)
            writer = csv.writer(csvoutput,lineterminator='\n')
            # si scrive l'header nel file di output
            writer.writerow(['Row', 'X1', 'Y1', 'X2', 'Y2', 'X3', 'Y3', 'AvgX', 'AvgY', 'Shot'])
            # si legge l'header nel file di input
            row = next(reader)

            try:
                while(True):

                    # lista contenente i nuovi elementi da andare a inserire all'interno della riga
                    new_row = []

                    # si legge la prima vera riga del file filtrato
                    row = next(reader)

                    # si inserisce come primo elemento il numero di riga
                    new_row.append(row[0])

                    # coordinate x1 x2 del primo/ultimo frame e y1 y2 del primo/ultimo frame di ogni intorno (5-5-5)
                    firstlast = [0, 0, 0, 0]

                    # contatore circolare (varrà 0/1/2)
                    ctrl = 0

                    # frame precedenti al colpo: k per scorrere tutti gli elementi dei frame della riga (pre colpo), ctrl per le sottocategorie (VIS,X,Y)
                    # k + 1 FONDAMENTALE per saltare il frame iniziale del numero di riga
                    for k in range(0, shot_start * 3):
                        first_last(ctrl, row, k + 1, firstlast)
                        ctrl = (ctrl + 1) % 3

                    # si appende nella nuova riga la differenza tra il primo e ultimo frame in coordinate x e y
                    # x_diff coordinate
                    new_row.append(round(firstlast[0] - firstlast[1], 3))
                    # y_diff coordinate
                    new_row.append(round(firstlast[2] - firstlast[3], 3))
                    
                    # media x e y FINESTRE CENTRALI [sumx,timesx,sumy,timesy], il primo è la somma, il secondo il contatore
                    avg = [0, 0, 0, 0]

                    # vengono riazzerete le coordinate x,y del primo/ultimo frame
                    firstlast = [0, 0, 0, 0]

                    # frame durante il colpo: k per scorrere tutti gli elementi dei frame della riga (durante il colpo), ctrl per le sottocategorie (VIS,X,Y)
                    for k in range(shot_start * 3, (shot_end * 3) + 3):
                        # k + 1 FONDAMENTALE per saltare il frame iniziale del numero di riga
                        first_last(ctrl, row, k + 1, firstlast, avg)
                        # ctrl può assumere solo 3 valori: 0 -> Vis, 1 -> x, 2 -> y 
                        ctrl = (ctrl + 1) % 3

                    # si appende nella nuova riga la differenza tra il primo e ultimo frame in coordinate x e y
                    # x_diff coordinate
                    new_row.append(round(firstlast[0] - firstlast[1], 3))
                    # y_diff coordinate
                    new_row.append(round(firstlast[2] - firstlast[3], 3))

                    # vengono riazzerete le coordinate x,y del primo/ultimo frame                                     
                    firstlast = [0, 0, 0, 0]

                    # frame post colpo: k per scorrere tutti gli elementi dei frame della riga (post colpo), ctrl per le sottocategorie (VIS,X,Y)
                    for k in range((shot_end * 3) + 3, window * 3):
                        # k + 1 FONDAMENTALE per saltare il frame iniziale del numero di riga
                        first_last(ctrl, row, k + 1, firstlast)
                        # ctrl può assumere solo 3 valori: 0 -> Vis, 1 -> x, 2 -> y 
                        ctrl = (ctrl + 1) % 3

                    # si appende nella nuova riga la differenza tra il primo e ultimo frame in coordinate x e y
                    # x_diff coordinate 
                    new_row.append(round(firstlast[0] - firstlast[1], 3))
                    # x_diff coordinate 
                    new_row.append(round(firstlast[2] - firstlast[3], 3))

                    # print(avg[0], avg[2])
                    # print(avg[1], avg[3])
                    new_row.append(round(avg[0] / avg[1], 3))
                    new_row.append(round(avg[2] / avg[3], 3))
                    # si appende il colpo
                    new_row.append(row[window * 3 + 1])

                    # si scrive la nuova riga nel file
                    writer.writerow(new_row)

            except Exception as e:
                print(e)


if __name__ == '__main__':
    main()
