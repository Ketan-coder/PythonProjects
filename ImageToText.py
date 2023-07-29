import cv2
#pytesseract needs some setup
import pytesseract

# Load the image using OpenCV
image = cv2.imread("Image.png") #jpg, jpeg, and png.

# Convert the image to grayscale
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Apply Otsu's thresholding to binarize the image
thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

# Pass the binarized image to Tesseract to extract text
text = pytesseract.image_to_string(thresh)

# Print the extracted text
print(text)
