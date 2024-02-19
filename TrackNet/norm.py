import csv
import sys

"""

Script che normalizza le coordinate della pallina nello spazio (quando visibile) rendendole indipendenti dalla risoluzione del video
 
"""

 
if len(sys.argv) != 3:
    print('run as: "python norm.py <input.csv> <output.csv> "')
    exit(1)

input = sys.argv[1]
output = sys.argv[2]
x_res = 1280
y_res = 720

# creo il nuovo csv con aggiunta la colonna 'Shot'
with open(input, 'r') as csvinput:
    with open(output, 'w+') as csvoutput:
        writer = csv.writer(csvoutput, lineterminator='\n')
        reader = csv.reader(csvinput)

        header = ['Frame', 'Vis', 'X', 'Y']
        writer.writerow(header)

        # lettura header
        header = next(reader)
        print(header)

        new_row = []

        for row in reader:

            # si inserisce il numero di riga
            new_row.append(row[0])

            # si controlla se la pallina risulta essere visibile
            if int(row[1]) != 0:
                # si inserisce la visibilità
                new_row.append(row[1])

                # si normalizzano le coordinate della pallina
                x_norm = round((int(row[2]) / x_res) * 100, 3)
                y_norm = round((int(row[3]) / y_res) * 100, 3)
                new_row.append(str(x_norm))
                new_row.append(str(y_norm))

                # # si inserisce 'Shot'
                # new_row.append(row[5])
            else: 
                # si inserisce la visibilità (che risulta essere 0)
                new_row.append(row[1])
                # si inseriscono le coordinate della pallina (che risultano essere 0)
                new_row.append(row[2])
                new_row.append(row[3])

            writer.writerow(new_row)

            new_row = []