import cvzone
import cv2 
#from menuAndSettings import settings

boxWidth, boxHeight = 45*3//2, 75*3//2

windowClose_png = cv2.imread("./Finestre_COIMBRA/CloseWindow.png", cv2.IMREAD_UNCHANGED)
windowClose_png = cv2.resize(windowClose_png, (boxWidth,boxHeight))


windowFocus_png = cv2.imread("./Finestre_COIMBRA/FocusWindow.png", cv2.IMREAD_UNCHANGED)
windowFocus_png = cv2.resize(windowFocus_png, (boxWidth,boxHeight))

windowOpen_png = cv2.imread("./Finestre_COIMBRA/OpenWindow.png", cv2.IMREAD_UNCHANGED)
windowOpen_png = cv2.resize(windowOpen_png, (boxWidth,boxHeight))

png_0 = cv2.imread("./Number_COIMBRA/Number0.png", cv2.IMREAD_UNCHANGED)
png_1 = cv2.imread("./Number_COIMBRA/Number1.png", cv2.IMREAD_UNCHANGED)
png_2 = cv2.imread("./Number_COIMBRA/Number2.png", cv2.IMREAD_UNCHANGED)
png_3 = cv2.imread("./Number_COIMBRA/Number3.png", cv2.IMREAD_UNCHANGED)
png_4 = cv2.imread("./Number_COIMBRA/Number4.png", cv2.IMREAD_UNCHANGED)
png_5 = cv2.imread("./Number_COIMBRA/Number5.png", cv2.IMREAD_UNCHANGED)
png_6 = cv2.imread("./Number_COIMBRA/Number6.png", cv2.IMREAD_UNCHANGED)
png_7 = cv2.imread("./Number_COIMBRA/Number7.png", cv2.IMREAD_UNCHANGED)
png_8 = cv2.imread("./Number_COIMBRA/Number8.png", cv2.IMREAD_UNCHANGED)
png_bomb = cv2.imread("./Number_COIMBRA/Bomb.png", cv2.IMREAD_UNCHANGED)

png_0 = cv2.resize(png_0, (boxWidth,boxHeight))
png_1 = cv2.resize(png_1, (boxWidth,boxHeight))
png_2 = cv2.resize(png_2, (boxWidth,boxHeight))
png_3 = cv2.resize(png_3, (boxWidth,boxHeight))
png_4 = cv2.resize(png_4, (boxWidth,boxHeight))
png_5 = cv2.resize(png_5, (boxWidth,boxHeight))
png_6 = cv2.resize(png_6, (boxWidth,boxHeight))
png_7 = cv2.resize(png_7, (boxWidth,boxHeight))
png_8 = cv2.resize(png_8, (boxWidth,boxHeight))
png_bomb = cv2.resize(png_bomb, (boxWidth,boxHeight))

png_numbers = [png_0, png_1, png_2, png_3, png_4, png_5, png_6, png_7, png_8, png_bomb]


class Window:
    def __init__(self, id_nm, pos, value, isOpen, onFocus, onFlag, png):
        self.id_nm = id_nm              # id, tupla (n,m), cioè (colonna, riga)
        self.pos = pos                  # position in pixel dell'ancor point
        self.value = value              # valore della finestra (0,1,2,3 o -1 se bomba)
        self.isOpen = isOpen            # bool, la finestrà è aperta?
        self.onFocus = onFocus          # bool, la finestrà è in focus? il puntatore è su di essa?
        self.onFlag = onFlag            # bool, la finestrà è in flag?  (da implementare)
        self.png = png                  # immagine 

    def changePng(self):
        # Setta il png a seconda dello status dell'immagine
        if (self.isOpen):
            if ((self.png).all != (windowOpen_png).all):    #Effettuo il cambio di png e di posizione, solo se non è già stato effettuato, così da evitarmi lo spostamento di posizione per ogni loop del while nel main
                self.png = windowOpen_png
                self.pos = (self.pos[0], self.pos[1])     
        else:
            status = (self.onFlag, self.onFocus)
            match status:
                case (1,0):   #closed, onflag, NOT on focus
                    self.png = windowFocus_png      #Create ONFLAG
                case (1,1): #closed, onflag, on focus
                    self.png = windowFocus_png      #Create ONFLAG-ONFOCUS
                case (0,1): #closed, NOT on flag, on focus
                    self.png = windowFocus_png 
                case (0,0): #closed
                    self.png = windowClose_png
 
        return self.png, self.pos
        
    def pngOverlayer(self, frame):
        # Setta il png del numero sull'immagine
        frame = cvzone.overlayPNG(frame, self.png, self.pos)       # Aggiunge l'immagine dello stato del nuovo png (aperto, chiuso, in focus)
        if (self.isOpen) and (self.value != 0): 
            number_png = png_numbers[int(self.value)]
            frame = cvzone.overlayPNG(frame, number_png, self.pos) # Aggiunge l'immagine del *numero*
        return frame