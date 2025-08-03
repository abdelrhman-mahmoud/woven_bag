import json
import json_repair
from langchain.schema.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field
from datetime import datetime
from PIL import Image
import base64
import io
from typing import Optional, List
from database.db_operations import insert_control_panel1_data



def parse_json(text):
    try:
        return json_repair.loads(text)
    except Exception:
        return None


prompt = """Analyze the provided control panel image from a machine used in woven bag manufacturing. Extract the following specific fields:

* CurrentDateTime: The date and time displayed on the screen (e.g., "DD.MM.YYYY HH:MM:SS").
* HDPE_factor: The first numeric value from the 'HDPE' section, interpreted as HDPE factor.
* PP_factor: The second numeric value from the 'HDPE' section, interpreted as PP factor.
* HDPE_Exponent: The first numeric value from the 'FACTOR' section, interpreted as HDPE exponent.
* PP_Exponent: The second numeric value from the 'FACTOR' section, interpreted as PP exponent.
* HDPE_OutputFactorMeltPump: The first numeric value displayed directly below the 'FACTOR' section, interpreted as HDPE output factor for melt pump.
* PP_OutputFactorMeltPump: The second numeric value displayed directly below the 'FACTOR' section, interpreted as PP output factor for melt pump.
* Titer_g_9000m: The large blue numeric value, interpreted as titer in [g/9000m].
* NumberOfTapes: The numeric value next to the large blue value, interpreted as the number of tapes.
* EdgeTrimSide_mm: The numeric value next to 'width', interpreted as edge trim per side in [mm].
* TapeWidth_mm: The numeric value next to 'T. film width', interpreted as tape width in [mm].
* CuttingWidth_mm: The numeric value next to 'Cutting width', interpreted as cutting width in [mm].
* TotalRatioTheoretical: The numeric value next to 'Total Ratio', interpreted as total ratio theoretical.
* TotalRatioActual: The numeric value next to 'Extend Ratio', interpreted as total ratio actual.
* StretchRatioActual: The numeric value next to 'Windup Ratio', interpreted as stretch ratio actual.
* CalculatedPumpRPM: The numeric value next to 'Pump Sum', interpreted as calculated pump RPM.
* RawMaterialPercentage: The percentage value listed under 'rawmaterial %', interpreted as raw material percentage.
* AdditivePercentage: The percentage values listed under 'additive 1-4 %', interpreted as additive percentages.
* Company: The company name displayed on the screen.
* ExtruderType: The extruder type displayed on the screen.
* ScrewType: The screw type displayed on the screen.
* DieType: The die type displayed on the screen.
* AlarmMessages: A list of all alarm/warning messages displayed on the screen, including their timestamps if available.

Return the data strictly as a JSON object with a single 'items' key containing a list of objects. Ensure all numeric values are numbers (not strings) and exclude units from the JSON values themselves, relying on the field descriptions for context. For any requested numeric measure that is not explicitly visible or clearly identifiable for a specific material (e.g., PP exponent if only HDPE values are present), return `null`. Do not include any additional text or explanations outside the JSON object.
"""

class ControlPanelData(BaseModel):
    CurrentDateTime: str = Field(..., description="The date and time displayed on the screen.")
    HDPE_factor: Optional[float] = Field(None, description="The first numeric value from the 'HDPE' section, interpreted as HDPE factor.")
    PP_factor: Optional[float] = Field(None, description="The second numeric value from the 'HDPE' section, interpreted as PP factor.")
    HDPE_Exponent: Optional[float] = Field(None, description="The first numeric value from the 'FACTOR' section, interpreted as HDPE exponent.")
    PP_Exponent: Optional[float] = Field(None, description="The second numeric value from the 'FACTOR' section, interpreted as PP exponent.")
    HDPE_OutputFactorMeltPump: Optional[float] = Field(None, description="The first numeric value displayed directly below the 'FACTOR' section, interpreted as HDPE output factor for melt pump.")
    PP_OutputFactorMeltPump: Optional[float] = Field(None, description="The second numeric value displayed directly below the 'FACTOR' section, interpreted as PP output factor for melt pump.")
    Titer_g_9000m: Optional[float] = Field(None, description="The large blue numeric value, interpreted as titer in [g/9000m].")
    NumberOfTapes: Optional[int] = Field(None, description="The numeric value next to the large blue value, interpreted as the number of tapes.")
    EdgeTrimSide_mm: Optional[float] = Field(None, description="The numeric value next to 'width', interpreted as edge trim per side in [mm].")
    TapeWidth_mm: Optional[float] = Field(None, description="The numeric value next to 'T. film width', interpreted as tape width in [mm].")
    CuttingWidth_mm: Optional[float] = Field(None, description="The numeric value next to 'Cutting width', interpreted as cutting width in [mm].")
    TotalRatioTheoretical: Optional[float] = Field(None, description="The numeric value next to 'Total Ratio', interpreted as total ratio theoretical.")
    TotalRatioActual: Optional[float] = Field(None, description="The numeric value next to 'Extend Ratio', interpreted as total ratio actual.")
    StretchRatioActual: Optional[float] = Field(None, description="The numeric value next to 'Windup Ratio', interpreted as stretch ratio actual.")
    CalculatedPumpRPM: Optional[float] = Field(None, description="The numeric value next to 'Pump Sum', interpreted as calculated pump RPM.")
    RawMaterialPercentage: Optional[float] = Field(None, description="The percentage value listed under 'rawmaterial %', interpreted as raw material percentage.")
    AdditivePercentage: List[float] = Field(..., description="The percentage values listed under 'additive 1-4 %', interpreted as additive percentages.")
    Company: str = Field(..., description="The company name displayed on the screen.")
    ExtruderType: Optional[str] = Field(None, description="The extruder type displayed on the screen.")
    ScrewType: Optional[str] = Field(None, description="The screw type displayed on the screen.")
    DieType: Optional[str] = Field(None, description="The die type displayed on the screen.")
    AlarmMessages: List[str] = Field(..., description="List of alarm/warning messages.")

class Items(BaseModel):
    items: List[ControlPanelData] = Field(..., min_items=1, description="List of control panel data entries")

def generate(image_path, llm):
    
    with Image.open(image_path) as img:
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    system_message = SystemMessage(content="""You are a helpful assistant specialized in extracting structured data from images of industrial control panels.
The user will provide an image of a control panel.
Your task is to extract all visible data points as specified in the Pydantic schema, adhering to the new interpretations of the fields.
Crucially, you must also identify any alarm messages, based on typical practices for woven bag manufacturing machinery.
Return the extracted information in strict JSON format under a key called 'items'.
Ensure numeric values are numbers (not strings) and exclude units where applicable in the JSON values, but retain them in your internal understanding to inform solutions.
For any requested numeric measure that is not explicitly visible or clearly identifiable for a specific material (e.g., PP exponent if only HDPE values are present), return `null`.
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

    try:
        response = llm.invoke([system_message, user_prompt])
    except Exception as e:
        print(f"Error calling LLM: {e}")

        return None

    json_response = parse_json(response.content)

    if json_response and 'items' in json_response:
        for item in json_response['items']:
            data = ControlPanelData(**item)
            insert_control_panel1_data(data)
        print("\nExtracted Control Panel Data (JSON):")
        print(json.dumps(json_response, indent=4, ensure_ascii=False))
    else:
        print("Failed to extract data or 'items' key not found in response.")
        print(f"Raw model response: {response.content}")

    
    return json_response

if __name__ == "__main__":
    image_path = r"images/1.jpg"
    print(f"Running data capture at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    generate(image_path)