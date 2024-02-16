import cv2
import pygame
from window import Window
import numpy as np
from random import randint, choice
import sys 

def are_adjacent(coord1, coord2):
    """
        Funzione per verificare se due coppie di coordinate A (x1,y1) e B (x2,y2) sono adiacenti
    """
    x1, y1 = coord1
    x2, y2 = coord2
    return abs(x1 - x2) <= 1 and abs(y1 - y2) <= 1

def zeroGrouper(zerosList):
    """
    Input:
    - Lista con tutte le coordinate (tuple) che corrispondono a cella con valore zero
    Output:
    - Dizionario che ha come valori, liste che contengono le coordinate (tuple) di zero adiacenti 
    """
    
    groups = {}    # Dizionario per salvare i raggruppamenti
    for COORD in zerosList:
        # Cerca in quali gruppi è adiacente questa coordinata
        found_groups_key = []   # Salvo in questa lista le chiavi dei gruppi trovati
        
        for group_key, group_coords in groups.items():
            if any(are_adjacent(COORD, group_coord) for group_coord in group_coords):   #Per ogni group_coord, ...controlla se COORD è adiacente ad almeno uno (ANY) 
                found_groups_key.append(group_key)
        
        # Se non è adiacente a nessun gruppo
        if len(found_groups_key) == 0:              
            new_group_key = "Group_"+str(len(groups))    # Creo la chiave del nuovo gruppo
            groups[new_group_key] = [COORD]             # Aggiungo la coordinata al dato gruppo
        
        # Se è adiacente ad un solo gruppo
        elif len(found_groups_key) == 1:                
            adiacent_group_key = found_groups_key[0]    # Grabbo la chiave del dato gruppo
            groups[adiacent_group_key].append(COORD)    # Aggiungo la coordinata al dato gruppo
        
        # Se è adiacente ad più gruppi
        else:                                           
            merged_group_key = found_groups_key[0]          # Grabbo la chiave del primo gruppo ---> al sua lista, aggiungerò gli elementi delle altre liste trovate                               

            for key_group in found_groups_key:          # Aggiungo gli elementi degli altri gruppi trovati al primo gruppo
                if key_group == found_groups_key[0]:    # Non concateno al merged_group il primo gruppo (in quanto già lo contiene)                
                    pass             
                else:
                    print(groups, merged_group_key, "\nAB", found_groups_key, key_group,"\n")
                    groups[merged_group_key] += groups[key_group]       # Concateno le altre liste alla prima lista trovata
                    groups.pop(key_group)                               # E rimuovo le date chiavi-liste dal dizionario groups  
    return groups
    
        
def gridWithValues(rows,cols, mines):
    """
    Take as input 
        - number of rows 
        - number of columns
        - number of mines 
    Returns: 
        - an 2d array of numbers that identify mines and relative numbers
        -  . . . . . . . . . . . . . . . . . . .
    """
    zerosList = []      #Lista con le coordinate di tutti gli zero esistenti

    #ERROR HANDLIIND
    #if mines > rows*cols: 
    #    print("\nERRORE: HAI INSERITO PIU' MINE CHE CELLE!\n")
    #    return 0

    # ------ Creo array con celle di zeri ------
    ARRAY = np.zeros((rows,cols))   
    
    # ------ Riempio l'array con le bombe (indicate da -1) ------
    buried_Mines = 0    #Contatore delle bombe "seppellite"
    for _ in iter(int, 1):
        y,x =   randint(0,rows-1), randint(0,cols-1)
        if ARRAY[y,x] != -1:
            ARRAY[y,x] = -1
            buried_Mines += 1
        if buried_Mines == mines: break

    
    # ------ Riempio le celle con i numeri ( = <numero di bombe adiacenti>) ------ 
    # ------ e riempio la lista zeroList

    # Loop per ogni cella dell'array, identificato dalla coppia x,y
    for y in range(rows):
        for x in range(cols):

            #Se questa cella non è una bomba
            if (ARRAY[y,x] != -1):
                # Controllo le 8 celle adiacenti identificate dalla coppia i,k
                # EVITO EFFETTO PACMAN ---> non considerando x,y uguali a -1  e   y=rows e x=cols 
                for k in [y for y in range(y-1,y+2) if (y != -1 and y != rows)]:
                    for i in [x for x in range(x-1,x+2) if (x != -1 and x != cols)]: 
                        if (k != y or i != x) and are_adjacent((y, x), (k, i)) and ARRAY[k, i] == -1:
                            ARRAY[y, x] += 1
                # Se il numero è ANCORA 0
                if (ARRAY[y,x] == 0): zerosList.append((x,y))
    
    return ARRAY, zerosList



def settings(NxM, mines, cap_width):
        
    #------ Dati relativi a dimensioni e distanza delle finestre -------------------------------------            
    ARRAY, zerosList = gridWithValues(NxM[1], NxM[0], mines)
    
    # Dizionario che ha come valori delle liste, le quali contengono le coordinate (tuple) di celle adiacenti 
    # le quali hanno come valore 0
    zeroGroup = zeroGrouper(zerosList)
    
    boxWidth = 45*3//2        # Base del box
    boxHeight = 75*3//2       # Altezza del box
    boxDistance_X = 20        # Distanza fra box su asse x
    boxDistance_Y = 20        # Distanza fra box su asse y

    #------- Dati relativi all'aspetto (iniziale) delle finestre -------------------------------------            
    windowClose_png = cv2.imread("./FinestreIMG/Chiusa-TipoC.png", cv2.IMREAD_UNCHANGED)
    windowClose_png = cv2.resize(windowClose_png, (boxWidth,boxHeight))

    #------- Creazione oggetti Windows -------------------------------------   
    x = (cap_width-(boxWidth+boxDistance_X)*(NxM[0])-boxDistance_X)//2
    rounded_x = round(x / 10) * 10         # L'origin deve avere una x con l'unità pari a 0, per evitare errori di calcolo
    origin = {"x": rounded_x , "y": 100 }  # Punto di ancoraggio del primo box (in alto a sx)
    
    AncorPointsList = []    # Array che contiene tutti i punti di ancoraggio
    AllWindows = []         # Array che contiene tutti gli oggetti Windows

    all_x = [origin["x"] + (i*(boxDistance_X+boxWidth)) for i in range(NxM[0])]
    all_y = [origin["y"] + (i*(boxDistance_Y+boxHeight)) for i in range(NxM[1])]

    m = -1
    for y in all_y:
        n = 0
        m += 1
        for x in all_x:
            ancorPoint = (x,y)
            AncorPointsList.append(ancorPoint)
            w = Window((n,m), ancorPoint, ARRAY[m,n], False, False, False, windowClose_png)
            AllWindows.append(w)
            n+= 1
            
    return AncorPointsList, zeroGroup, origin, all_x, all_y, AllWindows, boxWidth, boxHeight, boxDistance_X, boxDistance_Y     
        

def menu():
    """
        Permette di personalizzare il 
    """
    #Inizializzazione
    pygame.init()
    pygame.font.init()
    window_width, window_height = 500, 500
    screen = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption("MENU")

    black = (255, 255, 255)
    green = (0, 255, 0)

    # Variabili x posizione dei vari box di testo
    input_box_x = window_width // 2
    input_box_width = 75
    input_box_height = 50
    input_box1_y = window_height // 2 - input_box_width
    input_box2_y = window_height // 2
    input_box3_y = window_height // 2 + input_box_width
    
    # Variabili x posizione del bottone di inizializzazione gioco
    button_x = input_box_x - input_box_width 
    button_y = window_height // 2 + input_box_width*2
    
    # Initializzione proprietà dei box, ( attivo/ contenuto)
    input_box1 = pygame.Rect(input_box_x, input_box1_y, input_box_width, input_box_height) 
    input_text_columns = ""
    input_active_columns = False
    input_box2 = pygame.Rect(input_box_x, input_box2_y, input_box_width, input_box_height)
    input_text_Lines = ""
    input_active_lines = False
    input_box3 = pygame.Rect(input_box_x, input_box3_y , input_box_width, input_box_height)
    input_text_mines = ""
    input_active_mines = False
    
    button = pygame.Rect(button_x, button_y , input_box_width*2, input_box_height)

    # Iniz font
    fontTitle = pygame.font.Font(None, 48)
    font = pygame.font.Font(None, 36)
    fontInfo = pygame.font.Font(None, 25)

    # Iniz testi
    textTitle = fontTitle.render("Finestre Minate", True, (255, 255, 255))
    textTitle_rect = textTitle.get_rect(center=(window_width // 2, window_height // 6))
    textColumns = font.render("Colonne:   ", True, (255, 255, 255))
    textColumns_rect = textColumns.get_rect(topright=(input_box_x, input_box1_y + 10))
    textLines = font.render("Righe:   ", True, (255, 255, 255))
    textLines_rect = textLines.get_rect(topright=(input_box_x, input_box2_y + 10))
    textMines = font.render("Mine:   ", True, (255, 255, 255))
    textMines_rect = textMines.get_rect(topright=(input_box_x, input_box3_y + 10))
    
    run = True
    button_clicked = False  # Flag per track se il bottone è cliccato
    click_text = ""  # Testo da mostrare se il bottone è cliccato
    click_text_timer = 0  # Settaggio del timer
    click_text_lenght = 2500  # millisecondi per cui viene mostrato il testo

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                return 0
            
            # Al click del mouse...
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # ...controlla se il mouse è dentro il primo input box
                if input_box1.collidepoint(event.pos):
                    input_active_columns = True
                    input_active_lines = False  # Disattiva il secondo input box
                    input_active_mines = False  # Disattiva il terzo input box
                # ...controlla se il mouse è dentro il secondo input box
                elif input_box2.collidepoint(event.pos):
                    input_active_lines = True
                    input_active_columns = False  # Disattiva il primo input box
                    input_active_mines = False  # Disattiva il terzo input box
                # ...controlla se il mouse è dentro il terzo input box
                elif input_box3.collidepoint(event.pos):
                    input_active_mines = True
                    input_active_columns = False  # Disattiva il primo input box
                    input_active_lines = False  # Disattiva il secondo
                
                
                # ...controlla se il mouse è dentro il bottone
                elif button.collidepoint(event.pos):
                    # Condizioni non accettate
                    # 1 ----------------------------------------------------------------
                    if (input_text_columns == "") or (input_text_Lines == "" ) or (input_text_mines == ""):
                        button_clicked = True
                        click_text = fontInfo.render("Riempi tutti i box!", True, (255, 255, 255))
                        click_text_rect = click_text.get_rect(center=(window_width // 2, window_height // 6 + 40))
                        click_text_timer = pygame.time.get_ticks()  # Inizializza il timer
                    # 2 ----------------------------------------------------------------
                    elif (int(input_text_columns) > 12) or (int(input_text_Lines) > 4): 
                        button_clicked = True
                        click_text = fontInfo.render("Puoi inserire massimo 12 colonne e 4 righe!", True, (255, 255, 255))
                        click_text_rect = click_text.get_rect(center=(window_width // 2, window_height // 6 + 40))
                        click_text_timer = pygame.time.get_ticks()  # Inizializza il timer
                    # 3 ----------------------------------------------------------------
                    elif (int(input_text_columns) < 3) or (int(input_text_Lines) < 3): 
                        button_clicked = True
                        click_text = fontInfo.render("Le righe e le colonne devono essere almeno 3!", True, (255, 255, 255))
                        click_text_rect = click_text.get_rect(center=(window_width // 2, window_height // 6 + 40))
                        click_text_timer = pygame.time.get_ticks()  # Inizializza il timer
                    # 4 ----------------------------------------------------------------    
                    elif ( int(input_text_mines) > int(input_text_columns)*int(input_text_Lines) // 2):
                        button_clicked = True
                        click_text = fontInfo.render(f'Le mine devono essere meno delle metà celle! (<{int(input_text_columns)*int(input_text_Lines) // 2})', True, (255, 255, 255))
                        click_text_rect = click_text.get_rect(center=(window_width // 2, window_height // 6 + 40))
                        click_text_timer = pygame.time.get_ticks()  # Inizializza il timer
                    # 5 ----------------------------------------------------------------
                    elif ( int(input_text_mines) == 0):
                        button_clicked = True
                        click_text = fontInfo.render("Inserisci almeno una mina!", True, (255, 255, 255))
                        click_text_rect = click_text.get_rect(center=(window_width // 2, window_height // 6 + 40))
                        click_text_timer = pygame.time.get_ticks()  # Inizializza il timer
                    # ----------------------------------------------------------------
                    else:
                        button_clicked = True
                        click_text = fontInfo.render("Inizializzando il gioco...", True, (255, 255, 255))
                        click_text_rect = click_text.get_rect(center=(window_width // 2, window_height // 6 + 40))
                        click_text_timer = pygame.time.get_ticks()  # Inizializza il timer
                        
                        NxM = (int(input_text_columns), int(input_text_Lines))
                        mines = int(input_text_mines)
                        run = False
                        pygame.quit()  # Chiudi la finestra del menu

                        return False, NxM, mines
                    
      
                else:
                    input_active_columns = False
                    input_active_lines = False
                    input_active_mines = False

            elif event.type == pygame.KEYDOWN:
                if input_active_columns:
                    if event.key == pygame.K_BACKSPACE: input_text_columns = input_text_columns[:-1]
                    elif event.unicode.isdigit() and len(input_text_columns) < 3: input_text_columns += event.unicode
                elif input_active_lines:
                    if event.key == pygame.K_BACKSPACE: input_text_Lines = input_text_Lines[:-1]
                    elif event.unicode.isdigit() and len(input_text_Lines) < 3: input_text_Lines += event.unicode
                elif input_active_mines:
                    if event.key == pygame.K_BACKSPACE: input_text_mines = input_text_mines[:-1]
                    elif event.unicode.isdigit() and len(input_text_mines) < 3: input_text_mines += event.unicode
        

        # Fill the screen with a black color
        screen.fill((0, 0, 0))

        # Renderizzazione testi
        screen.blit(textTitle, textTitle_rect)
        screen.blit(textColumns, textColumns_rect)
        screen.blit(textLines, textLines_rect)
        screen.blit(textMines, textMines_rect)
        
        # Renderizzazione e primo box
        pygame.draw.rect(screen, green if input_active_columns else black, input_box1, 2)
        text_surface1 = font.render(input_text_columns, True, (255, 255, 255))
        text_rect1 = text_surface1.get_rect(center=(input_box_x+ input_box_width//2 , input_box1_y +25))
        screen.blit(text_surface1, text_rect1)

        # Renderizzazione e seconod box
        pygame.draw.rect(screen, green if input_active_lines else black, input_box2, 2)
        text_surface2 = font.render(input_text_Lines, True, (255, 255, 255))
        text_rect2 = text_surface2.get_rect(center=(input_box_x+ input_box_width//2, input_box2_y +25))
        screen.blit(text_surface2, text_rect2)
        
        # Renderizzazione e terzo box
        pygame.draw.rect(screen, green if input_active_mines else black, input_box3, 2)
        text_surface3 = font.render(input_text_mines, True, (255, 255, 255))
        text_rect3 = text_surface3.get_rect(center=(input_box_x+ input_box_width//2, input_box3_y +25))
        screen.blit(text_surface3, text_rect3)
        
        # Renderizzazione bottone
        pygame.draw.rect(screen, green, button, 2)
        button_text = font.render("Start Game", True, (255, 255, 255))
        button_text_rect = button_text.get_rect(center=button.center)  # Center the text within the button
        screen.blit(button_text, button_text_rect)

        # Renderizzazione del testo, se il bottone è cliccato
        if button_clicked:
            screen.blit(click_text, click_text_rect)
            current_time = pygame.time.get_ticks()
            if current_time - click_text_timer > click_text_lenght:  # Display for 2.5 seconds
                button_clicked = False
                
        # Update the display
        pygame.display.flip()