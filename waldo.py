import cv2
import random

def find_waldo():
    # Load the image
    random_image = get_random_image()

    image = cv2.imread(random_image)
    
    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Load the Waldo template image
    template = cv2.imread(random_image, 0)
    
    # Display the image with the rectangle
    cv2.imshow('Waldo', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows(1)
    

def get_random_image():
    image_list = ['A.jpg', 'B.jpg', 'C.jpg', 'D.jpg', 'E.jpg', 'F.jpg', 'G.jpg']
    
    # Select a random image from the list
    random_image = random.choice(image_list)
    
    return random_image

# Call the function to get a random image

# Path to the image containing Waldo
image_path = '1.jpg'

# Call the find_waldo function
find_waldo()
