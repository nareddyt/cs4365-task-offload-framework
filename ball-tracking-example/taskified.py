
import cv2
import imutils

# Define the lower and upper boundaries of the "green" ball in the HSV color space
greenLower = (29, 86, 6)
greenUpper = (64, 255, 255)

# grab a reference to the video file
vs = cv2.VideoCapture("./ball_tracking_example.mp4")

# Start defining tasks


def get_frame():

    # Grab the current frame
    frame = vs.read()[1]

    if frame is None:
        # End of video, stop execution
        return False, None

    # Resize to save space
    frame = imutils.resize(frame, width=600)

    return True, (frame)


def calculate_hsv(frame):

    # Blur and convert frame to the HSV color space
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    return True, (frame, hsv)


def calculate_mask(frame, hsv):

    # Construct a mask for the color "green"
    # Perform a series of dilations and erosions to remove any small blobs left in the mask
    mask = cv2.inRange(hsv, greenLower, greenUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    return True, (frame, mask)


def find_contours(frame, mask):

    # Find contours in the mask
    contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)

    if len(contours) == 0:
        # No contours found, stop execution
        return False, None

    return True, (frame, contours)


def calculate_circle(frame, contours):

    # Find the largest contour in the mask
    # Use it to compute the minimum enclosing circle and centroid
    c = max(contours, key=cv2.contourArea)
    ((x, y), radius) = cv2.minEnclosingCircle(c)
    M = cv2.moments(c)
    center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

    if radius <= 10:
        # Circle is false positive
        return False, None

    return True, (frame, x, y, radius, center)


def draw_circle(frame, x, y, radius, center):
    # Draw the circle and centroid on the frame
    cv2.circle(frame, (int(x), int(y)), int(radius),
               (0, 255, 255), 2)
    cv2.circle(frame, center, 5, (0, 0, 255), -1)

    return True, (frame)


def show_frame(frame):

    # show the frame to our screen
    cv2.imshow("Frame", frame)

    # Sleep a tiny amount before next draw
    cv2.waitKey(1)


# Export functions as tasks
init_tasks = [
    get_frame
]
intermediate_tasks = [
    calculate_hsv,
    calculate_mask,
    find_contours,
    calculate_circle,
    draw_circle
]
end_tasks = [
    show_frame
]
