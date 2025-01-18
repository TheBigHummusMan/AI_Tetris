import cv2
import mediapipe as mp

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True)

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()

    if not ret:
        break

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_frame)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            # Optional: Draw all detected landmarks on the face
            mp_drawing.draw_landmarks(
                image=frame,  # The original frame
                landmark_list=face_landmarks,  # Detected face landmarks
                connections=mp_face_mesh.FACEMESH_TESSELATION,  # Connections between landmarks
                landmark_drawing_spec=None,  # Skip drawing individual landmarks
                connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_tesselation_style(),
                # Style for connections
            )

            # Define landmark indices for the left and right eyes
            left_eye_landmarks = [33, 133, 160, 159, 158, 153, 144, 145, 153, 154, 155]
            right_eye_landmarks = [362, 263, 387, 386, 385, 384, 381, 380, 374, 373, 390]

            # Draw landmarks for each eye
            for eye_landmarks in [left_eye_landmarks, right_eye_landmarks]:
                for idx in eye_landmarks:
                    # Retrieve the x and y coordinates of the landmark
                    x = int(face_landmarks.landmark[idx].x * frame.shape[1])  # Scale x to image width
                    y = int(face_landmarks.landmark[idx].y * frame.shape[0])  # Scale y to image height

                    # Draw a small circle at each landmark
                    cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

    # Display the processed frame
    cv2.imshow("Eye Tracking with Mediapipe", frame)

    # Exit the loop if the user presses the 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture object and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()

