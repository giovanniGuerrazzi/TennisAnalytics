import cv2
import csv
import sys

"""

Questo script qua ci permette di ottenere il video con le annotazioni a achermo della tipologia di colpo: DIRITTO o ROVESCIO

"""

# funzione che permette di visualizzare a video la tipologia di colpo
def create_word_overlay(frame, word):
    if(word == 'DIRITTO'):
        # cv2.putText è una funzione di OpenCV che inserisce del testo in un'immagine o in un frame video
        # colore blu
        cv2.putText(frame, word, (1000, 100), cv2.FONT_HERSHEY_TRIPLEX, 2, (255, 0, 0), 3)
    if(word == 'ROVESCIO'):
        # cv2.putText è una funzione di OpenCV che inserisce del testo in un'immagine o in un frame video
        # colore rosso
        cv2.putText(frame, word, (100,  100), cv2.FONT_HERSHEY_TRIPLEX, 2, (50, 50, 255), 3)

    return frame

# funzione che ci permette di processare il video con il suo csv (dataset finale) ottenendo un nuovo video con le annotazioni a video
def process_video_with_csv(video_file, csv_file, output_file):
    # si ottengono informazioni inerenti al video prese in input come la risoluzione e gli fps
    video_capture = cv2.VideoCapture(video_file)
    # si ottengono i pixel presenti sull'asse delle y
    frame_width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    # si ottengono i pixel presenti sull'asse delle x
    frame_height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    # si ottiene il numero di frame (fps)
    fps = video_capture.get(cv2.CAP_PROP_FPS)

    # si definisce il codec FourCC da utilizzare per la compressione del video,'mp4v' indica che il formato di compressione scelto è MPEG-4 Visual.
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    # serve per andare a lavorare sul nuovo file per annotarci a video i colpi/rimbalzi
    video_writer = cv2.VideoWriter(output_file, fourcc, fps, (frame_width, frame_height))

    # apertura file csv
    with open(csv_file, 'r') as csvfile:
        csv_reader = csv.reader(csvfile)

        num_shot = 0

        i = 0
        for row in csv_reader:
            i += 1
            # si saltano le prime due righe: la prima contiene l'header e la seconda è la prima riga che non ha frame precedenti
            if i == 1 or i == 2:
                continue
            # si estrae frame per frame dal video
            ret, frame = video_capture.read()

            # si controlla il valore dell'ultima colonna e se abbiamo un DIRITTO si segnala a video
            if int(row[-1]) == 1:
                # Add the word overlay to the frame
                frame = create_word_overlay(frame, 'DIRITTO')
                num_shot += 1

            # si controlla il valore dell'ultima colonna e se abbiamo un ROVESCIO si segnala a video
            if int(row[-1]) == 2:
                # Add the word overlay to the frame
                frame = create_word_overlay(frame, 'ROVESCIO')
                num_shot += 1

            # si scrive la notazione nel video      
            video_writer.write(frame)

    # si chiude tutto
    video_capture.release()
    video_writer.release()
    cv2.destroyAllWindows()
    
    print(f'numero di colpi etichettati {num_shot}')


if(len(sys.argv) != 4):
    print('run as: "python VideoPrinter.py <video_tennis.mp4> <dataset_tennis.csv> <video_tennis_predict.mp4>"')
    exit(1)

video_file = sys.argv[1]
csv_file = sys.argv[2]
output_file = sys.argv[3]

# il video viene processato
process_video_with_csv(video_file, csv_file, output_file)
