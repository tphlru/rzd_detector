import base64
from groq import Groq
import json

def encode_image_to_base64(image_path):
    """Encodes an image from the given path to base64."""
    with open(image_path, "rb") as image_file:
        image_data = base64.b64encode(image_file.read()).decode('utf-8')
    return f"data:image/jpeg;base64,{image_data}"

def analyze_face_emotions(image_path, api_key):
    """Encodes the image and sends it for analysis to the Groq API."""
    IMAGE_DATA_URL = encode_image_to_base64(image_path)
    
    client = Groq(api_key=api_key)
    completion = client.chat.completions.create(
        model="llama-3.2-11b-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Analyse the images, paying attention to the face. Study the facial expressions, identifying emotions. Examine components of facial expression, context and other to get an estimate of the mixed emotion, its description and components. Identify micro-emotions and micro-expressions. Describe only people's emotions, do not describe the environment or other irrelevant information"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": IMAGE_DATA_URL
                        }
                    }
                ]
            },
        ],
        temperature=0.35,
        max_completion_tokens=1024,
        top_p=1,
        stream=False,
        stop=None,
    )
    
    return completion.choices[0].message.content


def analyze_face_emotions2(image_path, api_key, previous_message=""):
    """Encodes the image and sends it for analysis to the Groq API, incorporating the previous message."""    
    client = Groq(api_key=api_key)
    completion = client.chat.completions.create(
        model="llama-3.2-11b-vision-preview",
        messages=[
            {
                "role": "system",
                "content": (
                    "Extract the intensity of each detected emotion, list all emotions present, "
                    "and determine the predominant emotion. Additionally, assess the behavior "
                    "as 'good', 'normal', or 'suspicious (criminal)'. Format the output in JSON "
                    "with fields: 'emotions', 'intensities', 'dominant_emotion', 'behavior_assessment'."
                )
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": previous_message},
                ]
            },
        ],
        temperature=0.35,
        max_completion_tokens=1024,
        top_p=1,
        stream=False,
        stop=None,
    )
    
    response_text = completion.choices[0].message.content
    # try:
    #     response_json = json.loads(response_text)
    # except json.JSONDecodeError:
    #     response_json = {"error": "Invalid JSON response", "raw_response": response_text}
    
    return response_text

# Example usage
image_path = "/home/LaboRad/Downloads/3.jpg"
api_key = "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"
response = analyze_face_emotions(image_path, api_key)
response = analyze_face_emotions2(image_path, api_key, response)


print(response)
