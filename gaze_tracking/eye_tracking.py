def run_head_tracking(event_queue):

    import cv2
    import mediapipe as mp
    import numpy as np
    import math
    import time
    import os

    NOT_LOOKING_AWAY = -1
    LOOKING_AWAY_5 = 0
    LOOKING_AWAY_10 = 2

    looking_away_start_time = None
    looking_away_duration_threshold = 5
    consecutive_away_frames = 0
    max_tolerance_frames = 5
    looking = NOT_LOOKING_AWAY

    def calculate_angle(a, b, c):
        """Calculate the angle between three points."""
        ab = (b[0] - a[0], b[1] - a[1], b[2] - a[2])
        bc = (c[0] - b[0], c[1] - b[1], c[2] - b[2])
        dot_product = sum([ab[i] * bc[i] for i in range(3)])
        magnitude_ab = math.sqrt(sum([ab[i] ** 2 for i in range(3)]))
        magnitude_bc = math.sqrt(sum([bc[i] ** 2 for i in range(3)]))
        cos_angle = dot_product / (magnitude_ab * magnitude_bc + 1e-6)
        angle = math.acos(max(-1, min(1, cos_angle)))
        return math.degrees(angle)

    def detect_head_turn(face_landmarks, frame_width, frame_height):
        """Detect head orientation."""
        # Get key landmarks
        nose_tip = face_landmarks.landmark[1]
        left_eye = face_landmarks.landmark[33]
        right_eye = face_landmarks.landmark[263]
        left_ear = face_landmarks.landmark[234]
        right_ear = face_landmarks.landmark[454]

        # Convert landmarks to pixel coordinates
        def to_pixel(landmark):
            return (landmark.x * frame_width, landmark.y * frame_height, landmark.z * frame_width)

        nose_tip = to_pixel(nose_tip)
        left_eye = to_pixel(left_eye)
        right_eye = to_pixel(right_eye)
        left_ear = to_pixel(left_ear)
        right_ear = to_pixel(right_ear)

        # Calculate yaw (horizontal rotation)
        eye_center = ((left_eye[0] + right_eye[0]) / 2, (left_eye[1] + right_eye[1]) / 2, (left_eye[2] + right_eye[2]) / 2)
        yaw_angle = calculate_angle(left_ear, nose_tip, right_ear)

        # Calculate pitch (vertical tilt)
        pitch_angle = calculate_angle(left_eye, nose_tip, right_eye)

        # Calculate roll (side tilt)
        roll_angle = calculate_angle(left_eye, right_eye, (right_eye[0], left_eye[1], 0))  # Approximate roll

        # # Check thresholds
        # if abs(yaw_angle) > 30:  # Yaw threshold
        #     print("Head turned too far horizontally!")
        # if abs(pitch_angle) > 20:  # Pitch threshold
        #     print("Head tilted too far vertically!")
        # if abs(roll_angle) > 15:  # Roll threshold
        #     print("Head tilted sideways!")

        return yaw_angle, pitch_angle, roll_angle

    def crop_eye_region(frame, landmarks, indices):
        """Crop the eye region from the frame based on landmarks."""
        x_coords = [landmarks[idx].x * frame.shape[1] for idx in indices]
        y_coords = [landmarks[idx].y * frame.shape[0] for idx in indices]

        # Get bounding box for the eye
        x_min, x_max = int(min(x_coords)), int(max(x_coords))
        y_min, y_max = int(min(y_coords)), int(max(y_coords))

        padding = 5
        x_min, x_max = max(0, x_min - padding), min(frame.shape[1], x_max + padding)
        y_min, y_max = max(0, y_min - padding), min(frame.shape[0], y_max + padding)

        return frame[y_min:y_max, x_min:x_max], (x_min,x_max), (y_min,y_max)

    def preprocess_eye_region(eye_region):
        """Preprocess the cropped eye region."""
        if eye_region is not None and eye_region.size > 0:
            gray_eye = cv2.cvtColor(eye_region, cv2.COLOR_BGR2GRAY)
            gray_eye = cv2.equalizeHist(gray_eye)
            return gray_eye
        else:
            print("Error: Eye region is empty")
            return None


    def apply_thresholding(gray_eye):
        """Apply binary thresholding to detect the pupil."""
        _, threshold_eye = cv2.threshold(gray_eye, 50, 255, cv2.THRESH_BINARY_INV)
        return threshold_eye


    def detect_pupil_contour(threshold_eye):
        """Find the largest contour, which is likely the pupil."""
        contours, _ = cv2.findContours(threshold_eye, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            # Get the largest contour by area
            largest_contour = max(contours, key=cv2.contourArea)
            # Calculate the center and radius of the enclosing circle
            (x, y), radius = cv2.minEnclosingCircle(largest_contour)
            return (int(x), int(y)), int(radius)
        return None, None


    def detect_pupil_with_hough(gray_eye):
        """Detect the pupil using Hough Circle Transform."""
        circles = cv2.HoughCircles(
            gray_eye,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=20,
            param1=50,
            param2=30,
            minRadius=3,
            maxRadius=15
        )
        if circles is not None:
            circles = np.uint16(np.around(circles))
            return (circles[0, 0][0], circles[0, 0][1]), circles[0, 0][2]
        return None, None


    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True)

    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles

    if os.name == 'nt':
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    else:
        cap = cv2.VideoCapture(0)

    while cap.isOpened():
        ret, frame = cap.read()

        if not ret:
            break

        # Define eye landmarks
        left_eye_indices = [33, 133, 160, 159, 158, 153, 144, 145]
        right_eye_indices = [362, 263, 387, 386, 385, 384, 381, 380]

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_frame)

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                yaw, pitch, roll = detect_head_turn(face_landmarks, frame.shape[1], frame.shape[0])

                looking_away = False

                for eye_indices in [left_eye_indices, right_eye_indices]:
                    # Crop the eye region
                    eye_region = crop_eye_region(frame, face_landmarks.landmark, eye_indices)

                    # Preprocess the eye region
                    eye_region, x_coords, y_coords = eye_region
                    gray_eye = preprocess_eye_region(eye_region)

                    if gray_eye is None:
                        continue

                    # Apply thresholding
                    threshold_eye = apply_thresholding(gray_eye)

                    # Detect pupil using contours
                    pupil_center, pupil_radius = detect_pupil_contour(threshold_eye)

                    # Draw the detected pupil
                    if pupil_center and pupil_radius:

                        pupil_center = (pupil_center[0] + x_coords[0],pupil_center[1] + y_coords[0])
                        center = ((x_coords[0]+x_coords[1])/2, (y_coords[0] + y_coords[1])/2)

                        threshold_pupil_radius = pupil_radius

                        x_limit = (center[0] - threshold_pupil_radius, center[0] + threshold_pupil_radius)
                        y_limit = (center[1] - threshold_pupil_radius/1.5, center[1] + threshold_pupil_radius/1.5)

                        if not (x_limit[0] < pupil_center[0] < x_limit[1] and y_limit[0] < pupil_center[1] < y_limit[1]):
                            looking_away = True
                            break

                        cv2.circle(frame, pupil_center, int(pupil_radius), (0, 0, 255), 2)

                if looking_away:
                    if looking_away_start_time is None:
                        # Start the timer when the user first looks away
                        looking_away_start_time = time.time()
                        consecutive_away_frames = 1
                    else:
                        consecutive_away_frames += 1
                        looking_away_duration = time.time() - looking_away_start_time > looking_away_duration_threshold
                        if 10 > looking_away_duration > 5:
                            if looking != LOOKING_AWAY_5: event_queue.put("LOOKING_AWAY_5")
                        elif looking_away_duration > 10:
                            if looking != LOOKING_AWAY_10: event_queue.put("LOOKING_AWAY_10")
                else:
                    if 0 < consecutive_away_frames < max_tolerance_frames:
                        # Allow skipped frames without resetting the timer
                        consecutive_away_frames += 1
                    else:
                        # Reset tracking if user is no longer looking away
                        looking_away_start_time = None
                        consecutive_away_frames = 0
                        if looking != NOT_LOOKING_AWAY: event_queue.put("NOT_LOOKING_AWAY")

                # Optional: Draw all detected landmarks on the face
                mp_drawing.draw_landmarks(
                    image=frame,  # The original frame
                    landmark_list=face_landmarks,  # Detected face landmarks
                    connections=mp_face_mesh.FACEMESH_TESSELATION,  # Connections between landmarks
                    landmark_drawing_spec=None,  # Skip drawing individual landmarks
                    connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_tesselation_style(),
                    # Style for connections
                )

                # Define landmark indices for the left and right eyes\
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

