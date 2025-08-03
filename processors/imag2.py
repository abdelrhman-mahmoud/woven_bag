import json
import json_repair
from langchain.schema.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field
from datetime import datetime
from PIL import Image
import base64
import io
from typing import Optional, List
from database.db_operations import insert_control_panel2_data

def parse_json(text):
    try:
        return json_repair.loads(text)
    except:
        return None


prompt = """Analyze the provided control panel image from a machine used in woven bag manufacturing. Extract the following specific fields:

* **CurrentDateTime**: The date and time displayed on the screen (e.g., "DD.MM.YYYY HH:MM:SS").
* **OIL_HEATER_Target_Temp_1**: The target temperature for the first oil heater.
* **OIL_HEATER_Actual_Temp_1**: The actual temperature for the first oil heater.
* **OIL_HEATER_Target_Temp_2**: The target temperature for the second oil heater.
* **OIL_HEATER_Actual_Temp_2**: The actual temperature for the second oil heater.
* **HOT_AIR_Target_Temp**: The target temperature for the hot air section.
* **HOT_AIR_Actual_Temp**: The actual temperature for the hot air section.
* **ANNEALING_Percentage**: The annealing percentage.
* **Line_Speed_1**: The line speed from the first column.
* **Amperage_1**: The amperage from the first column.
* **Torque_1**: The torque from the first column.
* **Line_Speed_2**: The line speed from the second column.
* **Amperage_2**: The amperage from the second column.
* **Torque_2**: The torque from the second column.
* **Line_Speed_3**: The line speed from the third column.
* **Amperage_3**: The amperage from the third column.
* **Torque_3**: The torque from the third column.
* **AlarmMessages**: A list of all alarm/warning messages displayed on the screen, including their timestamps if available.

Return the data strictly as a JSON object with a single 'items' key containing a list of objects. Ensure all numeric values are numbers (not strings) and exclude units from the JSON values themselves, relying on the field descriptions for context. For any requested numeric measure that is not explicitly visible or clearly identifiable, return `null`. Do not include any additional text or explanations outside the JSON object.

Required JSON Format Example:
{
    "items": [
        {
            "CurrentDateTime": "",
            "OIL_HEATER_Target_Temp_1": null,
            "OIL_HEATER_Actual_Temp_1": null,
            "OIL_HEATER_Target_Temp_2": null,
            "OIL_HEATER_Actual_Temp_2": null,
            "HOT_AIR_Target_Temp": null,
            "HOT_AIR_Actual_Temp": null,
            "ANNEALING_Percentage": null,
            "Line_Speed_1": null,
            "Amperage_1": null,
            "Torque_1": null,
            "Line_Speed_2": null,
            "Amperage_2": null,
            "Torque_2": null,
            "Line_Speed_3": null,
            "Amperage_3": null,
            "Torque_3": null,
            "AlarmMessages": [],
        }
    ]
}
"""

class ControlPanelData2(BaseModel):
    CurrentDateTime: str = Field(..., description="The date and time displayed on the screen.")
    OIL_HEATER_Target_Temp_1: Optional[float] = Field(None, description="The target temperature for the first oil heater.")
    OIL_HEATER_Actual_Temp_1: Optional[float] = Field(None, description="The actual temperature for the first oil heater.")
    OIL_HEATER_Target_Temp_2: Optional[float] = Field(None, description="The target temperature for the second oil heater.")
    OIL_HEATER_Actual_Temp_2: Optional[float] = Field(None, description="The actual temperature for the second oil heater.")
    HOT_AIR_Target_Temp: Optional[float] = Field(None, description="The target temperature for the hot air section.")
    HOT_AIR_Actual_Temp: Optional[float] = Field(None, description="The actual temperature for the hot air section.")
    ANNEALING_Percentage: Optional[float] = Field(None, description="The annealing percentage.")
    Line_Speed_1: Optional[float] = Field(None, description="The line speed from the first column.")
    Amperage_1: Optional[float] = Field(None, description="The amperage from the first column.")
    Torque_1: Optional[float] = Field(None, description="The torque from the first column.")
    Line_Speed_2: Optional[float] = Field(None, description="The line speed from the second column.")
    Amperage_2: Optional[float] = Field(None, description="The amperage from the second column.")
    Torque_2: Optional[float] = Field(None, description="The torque from the second column.")
    Line_Speed_3: Optional[float] = Field(None, description="The line speed from the third column.")
    Amperage_3: Optional[float] = Field(None, description="The amperage from the third column.")
    Torque_3: Optional[float] = Field(None, description="The torque from the third column.")
    AlarmMessages: List[str] = Field(..., description="List of alarm/warning messages.")

class Items(BaseModel):
    items: List[ControlPanelData2] = Field(..., min_items=1, description="List of control panel data entries")

def generate(image_path, llm):
    
    with Image.open(image_path) as img:
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    system_message = SystemMessage(content="""You are a helpful assistant specialized in extracting structured data from images of industrial control panels.
        The user will provide an image of a control panel.
        Your task is to extract all visible data points as specified in the Pydantic schema, adhering to the new interpretations of the fields.
        Crucially, you must also identify any alarm messages, if applicable, based on typical practices for woven bag manufacturing machinery.
        Return the extracted information in strict JSON format under a key called 'items'.
        Ensure numeric values are numbers (not strings) and exclude units where applicable in the JSON values, but retain them in your internal understanding to inform solutions.
        For any requested numeric measure that is not explicitly visible or clearly identifiable, return `null`.
        Do not include any explanations, comments, or additional text outside the JSON object. Only return the JSON object.""")

    user_prompt = HumanMessage(content=[
        {
            "type": "text",
            "text": "\n".join([
                "## Pydantic Details:",
                json.dumps(Items.model_json_schema(), ensure_ascii=False),
                "",
                "## Story Details:",
                "```json",
                prompt
            ])
        },
        {
            "type": "image_url",
            "image_url": f"data:image/png;base64,{img_base64}"
        }
    ])

    response = llm.invoke([system_message, user_prompt])

    json_response = parse_json(response.content)

    if json_response and 'items' in json_response:
        for item in json_response['items']:
            data = ControlPanelData2(**item)
            insert_control_panel2_data(data)
        print("\nExtracted Control Panel Data (JSON):")
        print(json.dumps(json_response, indent=4, ensure_ascii=False))
    else:
        print("Failed to extract data or 'items' key not found in response.")
        print(f"Raw model response: {response.content}")

    
    return json_response

if __name__ == "__main__":
    image_path = r"images/2.jpg"
    print(f"Running data capture at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    generate(image_path)
