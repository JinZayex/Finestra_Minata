#----- Imports ---------------------------------------------
import cv2
import mediapipe as mp
import time
# Initialize MediaPipe Hands module
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
# Initialize OpenCV for video capture
cap = cv2.VideoCapture(0)  # 0 for the default webcam
#----------------------------------------------------------


#----- Window dimensions ---------------------------------------------
window_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
window_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print(f"Window dimensions: {window_width}x{window_height}")


pressed = False
start_time = None
prev_x = 0
prev_y = 0
clickThreshold = 1.2    # Dopo quanti secondi di focus su un elemento, attivo il click

# Function for time management
def clickHandler(x, y, prev_x, prev_y, start_time, pressed):
    """
        Se hoovering per tot tempo --> Click!
        Hovering all'interno di un range di tot pixel
    """
    x_range, y_range = 50,50
    if start_time is None:
        start_time = time.time()
        prev_x = x
        prev_y = y
    elif (x - x_range <= prev_x <= x + x_range) and (y - y_range <= prev_y <= y + y_range):
        #Here you're hovering
        print("Here you're hovering on", x,y)
        if time.time() - start_time >= clickThreshold:
            #Here you hovered so much that I pressed!
            print("YOU PRESSED!")
            pressed = True
    else:
        start_time = None
        pressed = False

    return prev_x, prev_y, start_time, pressed


def fingerPosTracker(frame):
    global prev_x, prev_y, start_time, pressed
    # Convert the image to grayscale (MediaPipe works better with grayscale images)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Detect hands in the image
    results = hands.process(frame_rgb)

    # Process the first detected hand
    if results.multi_hand_landmarks:
        first_hand_landmarks = results.multi_hand_landmarks[0]
        index_landmark = first_hand_landmarks.landmark[8]
        x = int(index_landmark.x * frame.shape[1])
        y = int(index_landmark.y * frame.shape[0])
        z = int(index_landmark.z * frame.shape[1])

        prev_x, prev_y, start_time, pressed = clickHandler(x, y, prev_x, prev_y, start_time, pressed)
        
        return x,y


while cap.isOpened():
    success, frame = cap.read()
    if not success:
        continue
    
    # Mirror the image horizontally to remove the mirror effect
    frame_flipped = cv2.flip(frame, 1)
    
    frame.fill(0)                                           # Schermo nero
    
    myBox = cv2.rectangle(frame, (100,100), (200,200), (255,0,0), 5)
    
    fingerPos = fingerPosTracker(frame_flipped)                     # Posizione indice
    
    if (fingerPos):                                                 
        myCircle = cv2.circle(frame, fingerPos, 20, (255, 0, 0), -1)           # Disegno cerchio in data posizione
        
        if (100<fingerPos[0]<200) and (100<fingerPos[1]<200):
                myBox = cv2.rectangle(frame, (100,100), (200,200), (255,255,255), 5) # "Accendo il box" = Il box è in focus 
                
                if (pressed):     
                    myCircle = cv2.circle(frame, fingerPos, 40, (255, 255, 0), -1)   # Ho "cliccato" sul box (il click corrisponde ad un focus prolungato nel tempo)
        
    
    cv2.imshow('Hand Tracking', frame)

    if cv2.waitKey(1) == ord('q'):
        print("Goodbye")
        break

cap.release()
cv2.destroyAllWindows()
