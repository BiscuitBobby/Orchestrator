from langchain_core.tools import tool
from Secrets.keys import google_api
import cv2
import google.generativeai as genai
import numpy as np
from PIL import Image

genai.configure(api_key=google_api)

def describe_image(query):
    cam = cv2.VideoCapture(0)
    ret, image = cam.read()
    cam.release()
    if not ret:
        raise Exception("Failed to capture image")
    objects_description = recognize_objects(image, query)
    return objects_description


# Convert a numpy array to a PIL image
def np_array_to_pil_image(image: np.ndarray) -> Image.Image:
    return Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))


# Recognize objects in the image using a generative model
def recognize_objects(image: np.ndarray, query="What is in this image"):
    pil_image = np_array_to_pil_image(image)
    model = genai.GenerativeModel(model_name="gemini-1.5-pro")
    prompt = query

    cv2.namedWindow('Image', cv2.WINDOW_GUI_NORMAL)
    cv2.imshow('Image', image)
    cv2.waitKey(1 * 1000)

    try:
        response = model.generate_content([pil_image, prompt]).text
    except Exception as e:
        response = e
    cv2.destroyAllWindows()
    return response

@tool(return_direct=True)
def CamImgTool(query):
    """Useful for recognizing objects, images and faces, using webcam or camera, can view what is in front of camera."""
    print("Starting recognition")
    response = describe_image(query)
    return response
