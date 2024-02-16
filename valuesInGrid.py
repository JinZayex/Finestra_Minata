import numpy as np
from random import randint, choice


def gridWithValues(rows,cols, mines):
    """
    Take as input 
        - number of rows 
        - number of columns
        - number of mines 
    Returns: 
        - an array of numbers that identify mines and relative numbers
    """
    #ERROR HANDLIIND
    if mines > rows*cols: 
        print("\nERRORE: HAI INSERITO PIU' MINE CHE CELLE!\n")
        return 0

    #Creo array con celle di zeri
    ARRAY = np.zeros((rows,cols))   
    
    #Riempio l'array con le bombe indicate da -1
    buried_Mines = 0
    for _ in iter(int, 1):
        y,x =   randint(0,rows-1), randint(0,cols-1)
        if ARRAY[y,x] != -1:
            ARRAY[y,x] = -1
            buried_Mines += 1
        if buried_Mines == mines: break

    # Loop per ogni cella dell'array, identificato dalla coppia x,y
    for y in range(rows):
        for x in range(cols):

            #Se questa cella non è una bomba
            if (ARRAY[y,x] != -1):
                
                # Controllo le 8 celle adiacenti identificate dalla coppia i,k
                # EVITO EFFETTO PACMAN ---> non considerando x,y uguali a -1  e   y=rows e x=cols 
                for k in [y for y in range(y-1,y+2) if (y != -1 and y != rows)]:
                    for i in [x for x in range(x-1,x+2) if (x != -1 and x != cols)]: 
                        if ARRAY[k,i] == -1:
                            ARRAY[y,x] += 1

                        
    print(ARRAY)
    return ARRAY

