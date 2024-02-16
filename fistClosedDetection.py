#----- Imports ---------------------------------------------
import cv2
import mediapipe as mp
import time
# Initialize MediaPipe Hands module
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
# Initialize OpenCV for video capture
cap = cv2.VideoCapture(0)  # 0 for the default webcam

#----- Window dimensions ---------------------------------------------
window_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
window_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print(f"Window dimensions: {window_width}x{window_height}")


def clickDetection(frame):
    # Convert the image to grayscale (MediaPipe works better with grayscale images)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Detect hands in the image
    results = hands.process(frame_rgb)

    # Process the first detected hand
    if results.multi_hand_landmarks:
        first_hand_landmarks = results.multi_hand_landmarks[0]
        
        index_landmark = first_hand_landmarks.landmark[8]
        middle_landmark = first_hand_landmarks.landmark[12]
        ring_landmark = first_hand_landmarks.landmark[16]
        pinky_landmark = first_hand_landmarks.landmark[20]
        wrist_landmark = first_hand_landmarks.landmark[0]
        
        index_mcp = first_hand_landmarks.landmark[5]
        middle_mpc = first_hand_landmarks.landmark[9]
        ring_mpc = first_hand_landmarks.landmark[13]
        pinky_mpc = first_hand_landmarks.landmark[17]
        
        wristDown = (wrist_landmark.y > index_mcp.y) and (wrist_landmark.y > middle_mpc.y) and (wrist_landmark.y>ring_mpc.y) and (wrist_landmark.y>pinky_mpc.y)
        underKnuckle= (index_landmark.y > index_mcp.y) and (middle_landmark.y > middle_mpc.y) and (ring_landmark.y > ring_mpc.y) and (pinky_landmark.y > pinky_mpc.y) 
        
        if wristDown and underKnuckle:
            cv2.putText(frame, "Fist detected!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "I see you hand...", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
  

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        continue
    
    clickDetection(frame)
    
    cv2.imshow('Hand Tracking', frame)

    if cv2.waitKey(1) == ord('q'):
        print("Goodbye")
        break

cap.release()
cv2.destroyAllWindows()
