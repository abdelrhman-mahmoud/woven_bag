import os
import json
import json_repair
from langchain.schema.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field
from datetime import datetime
from PIL import Image
import base64
import io
import mysql.connector
from typing import Optional, List
from database.db_operations import insert_control_panel4_data

def parse_json(text):
    try:
        return json_repair.loads(text)
    except Exception:
        return None

prompt = """Analyze the provided control panel image from a BSW MACHINERY tiraTex 1600 tape extrusion line. Extract the following specific fields:

* CurrentDateTime: The date and time displayed on the screen (e.g., "DD.MM.YYYY HH:MM:SS").
* LineSpeed_rpm: The line speed in rpm.
* CutTension_kg: The cutting tension in kg.
* ExtruderSpeed_rpm: The extruder speed in rpm.
* TakeOffSpeed_mpm: The take-off speed in m/min.
* FilmOscillation_mm: The film oscillation in mm.
* WaterExhaust_status: The status of the water exhaust (ON/OFF).
* WaterPump_status: The status of the water pump (ON/OFF).
* AlarmMessages: A list of all alarm/warning messages displayed on the screen, including their timestamps if available.

Return the data strictly as a JSON object with a single 'items' key containing a list of objects. Ensure all numeric values are numbers (not strings) and exclude units from the JSON values themselves, relying on the field descriptions for context. For any requested numeric measure that is not explicitly visible or clearly identifiable, return `null`. Do not include any additional text or explanations outside the JSON object.
"""

class ControlPanelData(BaseModel):
    CurrentDateTime: str = Field(..., description="The date and time displayed on the screen.")
    LineSpeed_rpm: Optional[float] = Field(None, description="The line speed in rpm.")
    CutTension_kg: Optional[float] = Field(None, description="The cutting tension in kg.")
    ExtruderSpeed_rpm: Optional[float] = Field(None, description="The extruder speed in rpm.")
    TakeOffSpeed_mpm: Optional[float] = Field(None, description="The take-off speed in m/min.")
    FilmOscillation_mm: Optional[float] = Field(None, description="The film oscillation in mm.")
    WaterExhaust_status: Optional[str] = Field(None, description="The status of the water exhaust (ON/OFF).")
    WaterPump_status: Optional[str] = Field(None, description="The status of the water pump (ON/OFF).")
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
            insert_control_panel4_data(data)
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
