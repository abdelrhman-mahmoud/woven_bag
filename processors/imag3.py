import os
import json
import json_repair
from langchain.schema.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field
from datetime import datetime
from PIL import Image
import base64
import io
from typing import Optional, List
from database.db_operations import insert_control_panel3_data

def parse_json(text):
    try:
        return json_repair.loads(text)
    except Exception:
        return None


prompt = """Analyze the provided control panel image from a BSW MACHINERY tiraTex 1600 tape extrusion line. Extract the following specific fields:

* CurrentDateTime: The date and time displayed on the screen (e.g., "DD.MM.YYYY HH:MM:SS").
* OilHeater1_Temp_C: The actual temperature of the first oil heater in degrees Celsius.
* OilHeater2_Temp_C: The actual temperature of the second oil heater in degrees Celsius.
* TotalRatio: The total ratio value.
* StretchRatio: The stretch ratio value.
* Annealing_percent: The annealing percentage values as a string.
* Godet1_speed_ms: The speed of the first godet in m/s.
* Godet1_temp_C: The temperature of the first godet in degrees Celsius.
* Godet2_speed_mpm: The speed of the second godet in m/min.
* Godet2_current_A: The current of the second godet in Amperes.
* Godet3_speed_mpm: The speed of the third godet in m/min.
* Godet3_current_A: The current of the third godet in Amperes.
* Godet4_speed_mpm: The speed of the fourth godet in m/min.
* Godet4_current_A: The current of the fourth godet in Amperes.
* Godet4_torque_percent: The torque of the fourth godet as a percentage.
* Extruder_speed_rpm: The extruder speed in rpm.
* Zone1_temp_C: The temperature of zone 1 in degrees Celsius.
* Zone1_pressure: The pressure in zone 1.
* Zone1_motor_load_percent: The motor load of zone 1 as a percentage.
* Zone2_temp_C: The temperature of zone 2 in degrees Celsius.
* Zone2_pressure: The pressure in zone 2.
* Zone2_motor_load_percent: The motor load of zone 2 as a percentage.
* Zone2_torque_percent: The torque of zone 2 as a percentage.
* AlarmMessages: A list of all alarm/warning messages displayed on the screen, including their timestamps if available.

Return the data strictly as a JSON object with a single 'items' key containing a list of objects. Ensure all numeric values are numbers (not strings) and exclude units from the JSON values themselves, relying on the field descriptions for context. Do not include any additional text or explanations outside the JSON object.
"""

class ControlPanelData(BaseModel):
    CurrentDateTime: str = Field(..., description="The date and time displayed on the screen.")
    OilHeater1_Temp_C: Optional[float] = Field(None, description="The actual temperature of the first oil heater in degrees Celsius.")
    OilHeater2_Temp_C: Optional[float] = Field(None, description="The actual temperature of the second oil heater in degrees Celsius.")
    TotalRatio: Optional[float] = Field(None, description="The total ratio value.")
    StretchRatio: Optional[float] = Field(None, description="The stretch ratio value.")
    Annealing_percent: Optional[str] = Field(None, description="The annealing percentage values as a string.")
    Godet1_speed_ms: Optional[float] = Field(None, description="The speed of the first godet in m/s.")
    Godet1_temp_C: Optional[float] = Field(None, description="The temperature of the first godet in degrees Celsius.")
    Godet2_speed_mpm: Optional[float] = Field(None, description="The speed of the second godet in m/min.")
    Godet2_current_A: Optional[float] = Field(None, description="The current of the second godet in Amperes.")
    Godet3_speed_mpm: Optional[float] = Field(None, description="The speed of the third godet in m/min.")
    Godet3_current_A: Optional[float] = Field(None, description="The current of the third godet in Amperes.")
    Godet4_speed_mpm: Optional[float] = Field(None, description="The speed of the fourth godet in m/min.")
    Godet4_current_A: Optional[float] = Field(None, description="The current of the fourth godet in Amperes.")
    Godet4_torque_percent: Optional[float] = Field(None, description="The torque of the fourth godet as a percentage.")
    Extruder_speed_rpm: Optional[float] = Field(None, description="The extruder speed in rpm.")
    Zone1_temp_C: Optional[float] = Field(None, description="The temperature of zone 1 in degrees Celsius.")
    Zone1_pressure: Optional[float] = Field(None, description="The pressure in zone 1.")
    Zone1_motor_load_percent: Optional[float] = Field(None, description="The motor load of zone 1 as a percentage.")
    Zone2_temp_C: Optional[float] = Field(None, description="The temperature of zone 2 in degrees Celsius.")
    Zone2_pressure: Optional[float] = Field(None, description="The pressure in zone 2.")
    Zone2_motor_load_percent: Optional[float] = Field(None, description="The motor load of zone 2 as a percentage.")
    Zone2_torque_percent: Optional[float] = Field(None, description="The torque of zone 2 as a percentage.")
    AlarmMessages: List[str] = Field(..., description="List of alarm/warning messages.")

class Items(BaseModel):
    items: List[ControlPanelData] = Field(..., min_items=1, description="List of control panel data entries")

def generate(image_path, llm):
    
    with Image.open(image_path) as img:
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    system_message = SystemMessage(content="""You are a helpful assistant specialized in extracting structured data from images of industrial control panels, specifically the BSW MACHINERY tiraTex 1600. 
The user will provide an image of a control panel. Your task is to extract all visible data points as specified in the Pydantic schema. Crucially, you must also identify any alarm messages, based on the tiraTex 1600 operating manual. Return the extracted information in strict JSON format under a key called 'items'. Do not include any explanations or comments.""")

    user_message = HumanMessage(content="\n".join([
        "## Pydantic Details:",
        json.dumps(Items.model_json_schema(), ensure_ascii=False),
        "",
        "## Instructions:",
        prompt
    ]))

    try:
        response = llm.invoke([
            system_message,
            user_message,
            HumanMessage(content=[
                {"type": "image_url", "image_url": f"data:image/png;base64,{img_base64}"}
            ])
        ])
    except Exception as e:
        print(f"Error calling LLM: {e}")

        return None

    json_response = parse_json(response.content)

    if json_response and 'items' in json_response:
        for item in json_response['items']:
            data = ControlPanelData(**item)
            insert_control_panel3_data(data)
        print("\nExtracted Control Panel Data (JSON):")
        print(json.dumps(json_response, indent=4, ensure_ascii=False))
    else:
        print("Failed to extract data or 'items' key not found in response.")
        print(f"Raw model response: {response.content}")

    
    return json_response

if __name__ == "__main__":
    image_path = r"images/3.jpg"
    print(f"Running data capture at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    generate(image_path)
