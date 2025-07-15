import streamlit as st
import pandas as pd
import os
import random
import re
from PIL import Image

# App settings
st.set_page_config(page_title="Wood Texture Survey", layout="wide")

# Load and shuffle images
@st.cache
def load_images(image_dir):
    images = []
    valid_extensions = ('.png', '.jpg', '.jpeg')
    for root, _, files in os.walk(image_dir):
        for file in files:
            if file.lower().endswith(valid_extensions):
                image_path = os.path.join(root, file)
                images.append((file, image_path))
    random.shuffle(images)
    return images

IMAGE_DIR = "Images"  # Make sure this folder is in your GitHub repo
images = load_images(IMAGE_DIR)

# Session state setup
if "index" not in st.session_state:
    st.session_state.index = 0
if "responses" not in st.session_state:
    st.session_state.responses = []

# Demographics form (first-time only)
if "demographics_collected" not in st.session_state:
    st.title("Demographic Information")
    with st.form("demographics_form"):
        age = st.text_input("Age")
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        experience = st.selectbox("Wood Experience", ["None", "Basic", "Average", "High", "Expert"])
        submitted = st.form_submit_button("Start Survey")

    if submitted:
        st.session_state["demographics"] = {
            "Age": age,
            "Gender": gender,
            "Wood Experience": experience
        }
        st.session_state["demographics_collected"] = True
        st.session_state["index"] = 0
        st.rerun()  # <--- Safe usage after button click
    else:
        st.stop()

# Main survey loop
if st.session_state.index < len(images):
    st.title(f"Image {st.session_state.index + 1} of {len(images)}")

    image_name, image_path = images[st.session_state.index]
    st.image(Image.open(image_path), caption=image_name, use_column_width=True)

    with st.form(f"form_{st.session_state.index}"):
        naturalness = st.selectbox("How natural does the texture appear to you?", ['Unnatural', 'Neutral', 'Natural'])
        aesthetic = st.slider("How much do you like the appearance? (0–6)", 0, 6, 3)
        sorting = st.selectbox("How would you rate the sorting of the texture?", [
            'Minimal Color Variation',
            'Slight Color Variation',
            'Moderate Color Variation',
            'Very Lively Color Variation',
            'Highly Lively Color Variation'
        ])
        submitted = st.form_submit_button("Next")

        if submitted:
            # Parse image filename
            pattern = r"wood_scale_(.*?)_distortion_(.*?)_roughness_(.*?)_knot_(.*?)_contrast_(.*?)_brightness_(.*?)_type_(.*?)\.png"
            match = re.match(pattern, image_name)
            if match:
                scale, distortion, roughness, knot, contrast, brightness, wood_type = match.groups()
            else:
                scale = distortion = roughness = knot = contrast = brightness = wood_type = None

            # Store response
            response = {
                **st.session_state.demographics,
                "Image": image_name,
                "Naturalness": naturalness,
                "Aesthetic": aesthetic,
                "Sorting": sorting,
                "Scale": scale,
                "Distortion": distortion,
                "Roughness": roughness,
                "Knot Effect": knot,
                "Contrast": contrast,
                "Brightness": brightness,
                "Wood Type": wood_type
            }

            st.session_state.responses.append(response)
            st.session_state.index += 1
            st.experimental_rerun()

# End screen
else:
    st.success("✅ Thank you! Your responses have been recorded.")
    df = pd.DataFrame(st.session_state.responses)
    st.write("### Your Results:")
    st.dataframe(df)

    # Allow download of results
    csv = df.to_csv(index=False)
    st.download_button("Download Responses", csv, file_name="results.csv", mime="text/csv")
