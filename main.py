import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from langchain.schema.messages import SystemMessage, HumanMessage
from PIL import Image
import base64
import io
import json

from processors.image1 import generate as generate_main_control_panel
from processors.imag2 import generate as generate_temperature_and_motor_data
from processors.extrusion_line_overview_processor import generate as generate_extrusion_line_overview
from processors.imag3 import generate as generate_godet_and_extruder_data

from processors.imag6 import generate as machine_3d
from processors.extruder_details_processor import generate as generate_extruder_details
load_dotenv()

def get_image_type(image_path , llm):

    with Image.open(image_path) as img:
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")


    system_message_content = """
    You are an assistant that identifies the type of a control panel image from a BSW MACHINERY tiraTex 1600 tape extrusion line.

    The user will provide an image of a control panel screen. Your task is to classify the image into one of the predefined categories below, based on the visible data elements.

    You must:
    - Carefully match the data fields visible in the image with each category.
    - Select a category only if at least 90% of its described data fields are clearly visible and identifiable in the image.
    - Return **only the number** corresponding to the matching category (1–6), or 7 if the image does not clearly fit any category.

    ### Categories:

    1: **Material and process configuration**
    - HDPE factor
    - PP factor
    - HDPE exponent
    - PP exponent
    - HDPE output factor for melt pump
    - PP output factor for melt pump
    - Titer (g/9000m)
    - Number of tapes
    - Edge trim per side (mm)
    - Tape width (mm)
    - Cutting width (mm)
    - Total ratio (theoretical and actual)
    - Stretch ratio (actual)
    - Calculated pump RPM
    - Raw material %
    - Additive percentages (1–4)
    - Company name
    - Extruder type, screw type, die type
    - Any alarm/warning messages

    2: **Temperature and motor performance**
    - Target/actual temps for 2 oil heaters
    - Target/actual hot air temperatures
    - Annealing %
    - Line speed
    - Amperage and torque for 3 lines (each with line speed, amp, torque)
    - Any alarm/warning messages

    3: **Godet and extrusion detail view**
    - CurrentDateTime
    - OilHeater1_Temp_C
    - OilHeater2_Temp_C
    - TotalRatio
    - StretchRatio
    - Annealing_percent
    - Godet1_speed_ms
    - Godet1_temp_C
    - Godet2_speed_mpm
    - Godet2_current_A
    - Godet3_speed_mpm
    - Godet3_current_A
    - Godet4_speed_mpm
    - Godet4_current_A
    - Godet4_torque_percent
    - Extruder_speed_rpm (if visible)
    - Zone1_temp_C
    - Zone1_pressure
    - Zone1_motor_load_percent
    - Zone2_temp_C
    - Zone2_pressure
    - Zone2_motor_load_percent
    - Zone2_torque_percent
    - AlarmMessages

    4: **Extrusion line process overview**
    - Line speed (m/min or rpm)
    - Cut tension (kg)
    - Extruder speed (rpm)
    - Take-off speed (m/min)
    - Film oscillation (mm)
    - Water exhaust status (ON/OFF) if shown
    - Water pump status (ON/OFF) if shown
    - Any alarm/warning messages (typically at the bottom of the screen)
    - A graphical diagram of the extrusion line is usually present with dynamic numeric data near machine icons

    5: **Alarm-focused operational summary**
    - Line speed (m/min)
    - Cut tension (kg)
    - Extruder speed (rpm)
    - Take-off speed (m/min)
    - Film oscillation (mm)
    - Water exhaust status (ON/OFF)
    - Water pump status (ON/OFF)
    - Extruder status (ON/OFF) based on 'EXTRUDER ON' button
    - Any alarm/warning messages

    6: **3D graphical overview with basic status and alarm**
    - Image contains a 3D-rendered graphical layout of the extrusion line
    - A visual display of key machines like the extruder, take-off, and cooling units
    - A digital clock showing the current date and time
    - A visible physical “EXTRUDER ON” button with indicator status (ON/OFF)
    - A single alarm or warning message visible at the bottom of the screen
    - No detailed numeric process data such as RPM, tension, temperature, or ratios

    7: **No match**
    - If none of the above categories are satisfied with at least 90% data field visibility.

    Return only a single integer value from 1 to 7.
    """
    system_message = SystemMessage(content=system_message_content)

    user_prompt = HumanMessage(content=[
        {
            "type": "image_url",
            "image_url": f"data:image/png;base64,{img_base64}"
        }
    ])

    response = llm.invoke([system_message, user_prompt])
    try:
        return int(response.content.strip())
    except (ValueError, TypeError):
        print("Error: The model did not return a valid number.")

def main():
    """Main function to run the program."""
    image_path = 'images/1.jpg'
    llm = ChatOllama(
    model="qwen3:4b",
    reasoning= False
    # temperature=0.2
)

    image_type = get_image_type(image_path, llm)
    print(f"Identified image type: {image_type}")

    if image_type == 1:
        generate_main_control_panel(image_path,llm)
    elif image_type == 2:
        generate_temperature_and_motor_data(image_path,llm)
    elif image_type == 3:
        generate_extrusion_line_overview(image_path,llm)
    elif image_type == 4:
        generate_godet_and_extruder_data(image_path, llm)
    elif image_type == 5:
        machine_3d(image_path,llm)
    elif image_type == 6:
        generate_extruder_details(image_path, llm)
    elif image_type == 'null':
        print("No valid image type identified.")
    else:
        print("Invalid image type.")

if __name__ == "__main__":
    main()