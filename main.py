#----- Imports ---------------------------------------------
import cv2
import mediapipe as mp
import cvzone
#from soundTest import playSound          momentaneusly not used
from menuAndSettings import menu, settings


NxM = (0,0)     # Tupla che contine colonee e righe        
mines = 0       # Mine
menuRun = True  # booleana che gestisce la run del menu
while menuRun:
    # Richiamo la funzione menu da menuAndSettings.py
    menuRun, NxM, mines = menu()
    
    
# Inizializzazione OpenCV per la cattura del video
cap = cv2.VideoCapture(0)  # 0 per la default webcam
cap_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)   # Dimensione del frame del video

#AncorPointsList,  # Array che contiene tutti i punti di ancoraggio delle finestre
#zeroGroup,        # Dizionario che ha come valori, liste che contengono le coordinate (tuple) di zero adiacenti 
#origin,           # Punto di ancoraggio della prima finestra in alto a sinistra
#all_x,            # Tutti i punti x di ancoraggio 
#all_y,            # Tutti i punti y di ancoraggio 
#AllWindows,       # Lista con tutti gli oggetti Windows
#boxWidth,         # Width della windows
#boxHeight,        # Height della windows
#boxDistance_X,    # Distanza X e fra windows
#boxDistance_Y     # Distanza Y e fra windows


AncorPointsList, zeroGroup, origin,all_x, all_y,AllWindows,boxWidth,boxHeight, boxDistance_X,    boxDistance_Y = settings(NxM, mines, cap_width)


# Inizializzazione MediaPipe Hands module
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

#----------------------------------------------------------


pressed = False                     # Variabile di controllo 

def handPosTracker(frame):
    """
    La funzione restituisce la posizione x,y dell'indice in px
    """
    global pressed
    # Conversione dell'immagine in grayscale (MediaPipe works better with grayscale images)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Detection della mano nell'immagine
    results = hands.process(frame_rgb)

    # Process the first detected hand
    if results.multi_hand_landmarks:
        first_hand_landmarks = results.multi_hand_landmarks[0]
        index_landmark = first_hand_landmarks.landmark[0]   # Ritorna un valore compreso fra 0 e 1
        x = int(index_landmark.x * frame.shape[1])          # Trasformo il valore 0-1 in pixel ---> Dal range [0-1] a [0-width]
        y = int(index_landmark.y * frame.shape[0])          # Trasformo il valore 0-1 in pixel ---> Dal range [0-1] a [0-height]
        #z = int(index_landmark.z * frame.shape[1])
        
        return x,y


def clickDetection(frame):
    """ 
    Il click corrisponde alla "chiusura della mano", cioè:
    • I landmarks delle falangette devono essere più in basso rispetto ai landmarks delle falangi 
      (= l'asse y delle falangette sarà maggiore)
      
    E' importante notare come, con queste premesse, nella detection di un braccio disteso verso il basso
    le falangette si trovano "sotto" le falangi (anche nel caso in cui la mano non sia chiusa), 
    venendo comunque calcolato come "chiusura della mano" .
    
    Si è ovviato a questo problema con la detection della posizione del polso. 
    
    Dunque...
    per alleggerire il calcolo (evitare di calcolare tutti i landmarks e metterli in relazione) 
    si è scelto di far valere come click la seguente situazione:
    • Falangetta-indice sotto falange-indice
    • Falangetta-mignolo sotto falange-mignolo
    • polso sotto falangia-ditoMedio
    """
    # Convert the image to grayscale (MediaPipe works better with grayscale images)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Detect hands in the image
    results = hands.process(frame_rgb)

    # Process the first detected hand
    if results.multi_hand_landmarks:
        first_hand_landmarks = results.multi_hand_landmarks[0]
        hand = first_hand_landmarks
        #index_landmark = first_hand_landmarks.landmark[8]
        #middle_landmark = first_hand_landmarks.landmark[12]
        #ring_landmark = first_hand_landmarks.landmark[16]
        #pinky_landmark = first_hand_landmarks.landmark[20]
        #wrist_landmark = first_hand_landmarks.landmark[0]
        
        #index_mcp = first_hand_landmarks.landmark[5]
        #middle_mpc = first_hand_landmarks.landmark[9]
        #ring_mpc = first_hand_landmarks.landmark[13]
        #pinky_mpc = first_hand_landmarks.landmark[17]
        
        #Controlla se le falangette sono sotto le nocche
        #wristDown = (wrist_landmark.y > index_mcp.y) and (wrist_landmark.y > middle_mpc.y) and (wrist_landmark.y>ring_mpc.y) and (wrist_landmark.y>pinky_mpc.y)
        #wristDown = (wrist_landmark.y > middle_mpc.y)
        #Controlla se il polso è sotto le nocche
        #underKnucle= (index_landmark.y > index_mcp.y) and (pinky_landmark.y > pinky_mpc.y) 
        
        #falanx = [8,20]    #lista id falangine
        #knucles = [5,17]   #lista id falangi (kno)
 
        if (hand.landmark[8].y >= hand.landmark[5].y):              # Falangetta-indice sotto falange-indice?
            if (hand.landmark[20].y >= hand.landmark[17].y):        # Falangetta-mignolo sotto falange-mignolo?
                if (hand.landmark[0].y >= hand.landmark[9].y):      # polso sotto falangia-ditoMedio?
                    return True



def which_n(mx, origin, boxWidth, boxDistance_X, NxM):
    """
    [0,              w] --> [0]
    [  w+d,    (w+d)+w] --> [1]
    [2(w+d),  2(w+d)+w] --> [2]
    [3(w+d),  3(w+d)+w] --> [3]
    [n(w+d),  n(w+d)+w] --> [n]
    """
    # Loop per tutte le colonne, fino a trovare, se c'è, la colonna (n) in cui si trova il puntatore
    for n in range(NxM[0]):
        a = n*(boxWidth+boxDistance_X)          + origin["x"] # Punto di ancoraggio dell'n-esimo box (asse x)
        b = n*(boxWidth+boxDistance_X)+boxWidth + origin["x"] # Punto di "arrivo" dell'n-esimo box  (asse x)
        if a <= mx <= b:
            break
        else:
            n = None
    return n
            
        

def which_m(my, origin, boxHeight, boxDistance_Y, NxM):
    """
    [0,              h] --> [0]
    [  h+d,    (h+d)+h] --> [1]
    [2(h+d),  2(h+d)+h] --> [2]
    [3(h+d),  3(h+d)+h] --> [3]
    [m(h+d),  m(h+d)+h] --> [m]
    """
    
    # Loop per tutte le righe, fino a trovare, se c'è, la righa (m) in cui si trova il puntatore
    for m in range(NxM[1]):
        a = m*(boxHeight+boxDistance_Y)             + origin["y"]   # Punto di ancoraggio dell'n-esimo box (asse y)
        b = m*(boxHeight+boxDistance_Y)+boxHeight   + origin["y"]   # Punto di "arrivo" dell'n-esimo box  (asse y)
        if a <= my <= b:
            break
        else:
            m = None
    return m 


def openZeros(coord, zerogroup, AllWindows):
    """
    Funzione che apre tutte le finestre che ''contengono'' 0 
    e le finestre che ''contengono'' 0 adiacenti
    """
    print("OPEN ZERO!")
    for group_key, group_list in zerogroup.items():         # Per ogni lista nella lista di liste di zero
        print(coord, group_key, group_list)
        if coord in group_list:          # Trova la lista nella quale risiede la coordinata <coord>
            print("The coord",coord, "is founded in",group_list)
            for i in group_list:         # E ogni coordinata di quella lista
                index = i[1]*NxM[0] + i[0]
                windowToOpen = AllWindows[index]
                windowToOpen.isOpen = True        # Dovrà APRIRE la finestra relativa
    return AllWindows
    
def openBombs(AllWindows):
    "'Apre' tutte le finestre che nascondono bombe"
    for w in AllWindows:
        if w.value == -1:
            w.isOpen = True
    
#--------------------------------------------------------            
#-------------------  Main loop -------------------------------------   
#--------------------------------------------------------   
windows_open = 0
gameWon = False
bombClicked = False    
              
while cap.isOpened():
    success, frame = cap.read()
    if not success:
        continue
    
    # Mirror the image horizontally to remove the mirror effect
    frame_flipped = cv2.flip(frame, 1)
    frame.fill(0)  
    
    # -------   Disegno rettangoli  e cerchio (puntatore)  ---------------------------------------------------------
    # Disegno rettangoli
    for ancor in AncorPointsList:
        myBox = cv2.rectangle(frame, (ancor[0], ancor[1]), (boxWidth+ancor[0], boxHeight+ancor[1]), (255,0,0), 5)
    
    # Reset all the windows to unfocus
    for w in AllWindows:
        w.onFocus = False
    
    # Disegno cerchio
    handPos = handPosTracker(frame_flipped)                     # Posizione della mano
    pressed = False
    
    if (handPos): 
        mx, my = handPos[0], handPos[1]                                 # Posizione del cerchio/mano/puntatore in pixel
        myCircle = cv2.circle(frame, (mx,my), 20, (0, 0, 255), -1)      # Disegno cerchio in data posizione
        
        n = which_n(mx, origin, boxWidth, boxDistance_X, NxM)         # Ritorna colonna selezionata (colonna 1, colonna2)
        m = which_m(my, origin, boxHeight, boxDistance_Y, NxM)        # Ritorna riga selezionata    (colonna 3, colonna 4)

        # Hovering
        if (n != None) and (m != None):
            hovered_box = cv2.rectangle(frame, (all_x[n],all_y[m]), (all_x[n]+boxWidth, all_y[m]+boxHeight), (255,255,255), 5) # "Accendo il box" = Il box è in focus 

            # Change in focus state the hovered window
            hovered_index = m*NxM[0] + n                    # Index della finestra "hoverata"
            focused_window = AllWindows[hovered_index]      # Grabbo l'oggetto della finestra "hoverata"
            focused_window.onFocus = True                   # ... e setto il suo attributo onFocus a True
            
            if (focused_window.isOpen != True):     # Check pression if the window is closed!
                pressed = clickDetection(frame_flipped)
            
            # Click 
            if (pressed):                  
                myCircle = cv2.circle(frame, handPos, 60, (255, 255, 0), -1)   # Modifico il cerchio se è avvenuto il clic
                
                clicked_window = focused_window
                clicked_window.isOpen = True
                
                # Se hai cliccato su una finestra che ha come valore 0
                if clicked_window.value == 0:
                    # "Apri" tutte le finestre adiacenti alla finestra corrente che hanno 0 come valore
                    zeroCellTuple = clicked_window.id_nm 
                    openZeros(zeroCellTuple, zeroGroup, AllWindows)

                # Se hai cliccato su una finestra che ha come valore -1 (bomba)
                if clicked_window.value == -1:
                    bombClicked = True
                    openBombs(AllWindows)    # Apri tutte le finestre che hanno come valore le bombe
                
                # Setta il numero corrente di finestre aperte
                i = 0
                for w in AllWindows:
                    if (w.isOpen): 
                        i += 1
                windows_open = i
                                    

    # -------------------------------------------------------------------------------------------------

    # Disegna sul frame ogni singola finestra 
    for w in AllWindows:
        w.changePng()
        frame = w.pngOverlayer(frame)
    

    if (bombClicked) and (gameWon == False):   # Se hai cliccato su una bomba
        cv2.putText(frame, "You lost!", (frame.shape[0]- 150 ,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 4)
    else:
        if (windows_open >= len(AllWindows)-mines):     # Se hai cliccato su tutte le celle che non sono zeri, hai vinto
            cv2.putText(frame, "You won! ", (frame.shape[0]- 250 ,50), cv2.FONT_HERSHEY_SIMPLEX, 3, (0,255,0), 4)
            gameWon = True
        else:
            cv2.putText(frame, "Window to open: "+str(len(AllWindows)-windows_open), (frame.shape[0]- 250 ,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 4)
    cv2.imshow('Hand Tracking', frame)




    if cv2.waitKey(1) == ord('q'):
        print("Goodbye")
        break
    
    if cv2.waitKey(10) == ord("p"):
        print("\n\nShowing information\nYou pressed p: ")
        for w in AllWindows:
            print(w.id_nm, w.pos, w.isOpen, w.onFocus, w.onFlag)
        print("-------")
    


cap.release()
cv2.destroyAllWindows()
