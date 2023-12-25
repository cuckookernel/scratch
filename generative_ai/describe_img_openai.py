import errno
import time
from pathlib import Path

from dotenv import load_dotenv
from openai import ChatCompletion

import base64

load_dotenv("/home/teo/profile.env")
# %%


def generate_img_msg(image_path: Path) -> list[dict[str, str]]:
    base64_image = encode_image(image_path)

    img_type = image_path.suffix.lstrip('.')
    print(f"img_type: {img_type}")
    return [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Describe this image"},
                {
                    "type": "image_url",
                    "image_url": f"data:image/{img_type};base64,{base64_image}",
                },
            ],
        },
    ]
# %%


def analyze_image(image_path: str) -> str:
    # %%
    img_msg = generate_img_msg(image_path)
    response = ChatCompletion.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "system",
                "content": """
                You are Sir David Attenborough. Narrate the picture of the human as if it is a 
                nature documentary. Make it snarky and funny. Don't repeat yourself. Make it short. 
                If I do anything remotely interesting, make a big deal about it!
                """,
            },
        ]
        # + script
        + img_msg,
        max_tokens=500,
    )
    response_text = response.choices[0].message.content
    print(response_text)
    # %%
    return response_text
    # %%


def encode_image(image_path: Path) -> str:
    while True:
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")
        except IOError as e:
            if e.errno != errno.EACCES:
                # Not a "file in use" error, re-raise
                raise
            # File is being written to, wait a bit and retry
            time.sleep(0.1)
# %%


def main():
# path to your image
    image_path = Path('/home/teo/Downloads/monis-flores.jpeg')
"""
Ah, here we observe a most peculiar specimen in what appears to be their natural habitat: the elusive festival homo sapiens. Adorned with flamboyant eyewear resembling the vibrant flowers of a tropical paradise, this individual signals a readiness to partake in the ceremonial festivities. Note the vibrant necklace — a classic display of this species' fondness for adornment and flair. And most captivating of all, the garb, featuring a trompe-l'œil of its own physical essence on a textile canvas. Such deceptive artistry! A camouflage? A bold fashion statement? Or perhaps a humorous challenge to the very fabric of reality itself! Oh, and look! A slight tilting of the head — what an extraordinary event! Truly, such bewildering behavior captivates the imagination and is the stuff of legend.
"""
    image_path = Path('/home/teo/Downloads/gladis-3-años.jpeg')
# getting the base64 encoding


script = []
# script
# analysis
# analyze posture
print("👀 David is watching...")
analysis = analyze_image(base64_image, script=script)

print("🎙️ David says:")
print(analysis)
