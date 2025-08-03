import os
from dotenv import load_dotenv
import json
import json_repair
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field
from datetime import datetime
from PIL import Image
import base64
import io
import mysql.connector
from typing import Optional, List

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY is not set in the environment variables.")

def parse_json(text):
    try:
        return json_repair.loads(text)
    except Exception:
        return None

def initialize_database():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password= "#ahlawy#bod@74#"
    )
    with conn.cursor() as c:
        c.execute("CREATE DATABASE IF NOT EXISTS control_panel_db")
        c.execute("USE control_panel_db")
        c.execute("DROP TABLE IF EXISTS control_panel8")
        c.execute('''CREATE TABLE IF NOT EXISTS control_panel8 (
            id INT PRIMARY KEY AUTO_INCREMENT,
            CurrentDateTime TEXT,
            JD_PR18_SV REAL,
            JD_PR18_PV REAL,
            JD_950F_P_main_display REAL,
            JD_950F_P_secondary_display REAL,
            YellowLight_status TEXT,
            GreenLight_status TEXT,
            RedLight_status TEXT
        )''')
    conn.commit()
    return conn

def insert_data(conn, data):
    with conn.cursor() as c:
        c.execute('''INSERT INTO control_panel8 (CurrentDateTime, JD_PR18_SV, JD_PR18_PV, JD_950F_P_main_display, JD_950F_P_secondary_display, YellowLight_status, GreenLight_status, RedLight_status)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''',
                  (data.CurrentDateTime, data.JD_PR18_SV, data.JD_PR18_PV, data.JD_950F_P_main_display, data.JD_950F_P_secondary_display, data.YellowLight_status, data.GreenLight_status, data.RedLight_status))
    conn.commit()

prompt = """Analyze the provided control panel image. The image shows two separate control panels, a 'JIADI JD-PR18' and a 'JIADI JD-950F-P', along with three indicator lights. Extract the following specific fields:

* CurrentDateTime: The date and time the image was taken, which is provided in the image metadata.
* JD_PR18_SV: The 'SV' value from the 'JIADI JD-PR18' controller.
* JD_PR18_PV: The 'PV' value from the 'JIADI JD-PR18' controller.
* JD_950F_P_main_display: The main display value from the 'JIADI JD-950F-P' controller.
* JD_950F_P_secondary_display: The secondary display value from the 'JIADI JD-950F-P' controller.
* YellowLight_status: The status of the yellow indicator light (ON/OFF).
* GreenLight_status: The status of the green indicator light (ON/OFF).
* RedLight_status: The status of the red indicator light (ON/OFF).

Return the data strictly as a JSON object with a single 'items' key containing a list of objects. Ensure all numeric values are numbers (not strings) and exclude units from the JSON values themselves, relying on the field descriptions for context. For any requested numeric measure that is not explicitly visible or clearly identifiable on the screen, return `null`. Do not include any additional text or explanations outside the JSON object.
"""

class ControlPanelData(BaseModel):
    CurrentDateTime: str = Field(..., description="The date and time the image was taken.")
    JD_PR18_SV: Optional[float] = Field(None, description="The 'SV' value from the 'JIADI JD-PR18' controller.")
    JD_PR18_PV: Optional[float] = Field(None, description="The 'PV' value from the 'JIADI JD-PR18' controller.")
    JD_950F_P_main_display: Optional[float] = Field(None, description="The main display value from the 'JIADI JD-950F-P' controller.")
    JD_950F_P_secondary_display: Optional[float] = Field(None, description="The secondary display value from the 'JIADI JD-950F-P' controller.")
    YellowLight_status: Optional[str] = Field(None, description="The status of the yellow indicator light (ON/OFF).")
    GreenLight_status: Optional[str] = Field(None, description="The status of the green indicator light (ON/OFF).")
    RedLight_status: Optional[str] = Field(None, description="The status of the red indicator light (ON/OFF).")

class Items(BaseModel):
    items: List[ControlPanelData] = Field(..., min_items=1, description="List of control panel data entries")

def generate(image_path):
    conn = initialize_database()
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=GOOGLE_API_KEY,
    )

    with Image.open(image_path) as img:
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    system_message = SystemMessage(content="""You are a helpful assistant specialized in extracting structured data from images of industrial control panels. 
The user will provide an image of a control panel. Your task is to extract all visible data points as specified in the Pydantic schema. Return the extracted information in strict JSON format under a key called 'items'. Do not include any explanations or comments.""")

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
        conn.close()
        return None

    json_response = parse_json(response.content)

    if json_response and 'items' in json_response:
        for item in json_response['items']:
            data = ControlPanelData(**item)
            insert_data(conn, data)
        print("\nExtracted Control Panel Data (JSON):")
        print(json.dumps(json_response, indent=4, ensure_ascii=False))
    else:
        print("Failed to extract data or 'items' key not found in response.")
        print(f"Raw model response: {response.content}")

    conn.close()
    return json_response

if __name__ == "__main__":
    image_path = r"images/8.jpg"
    print(f"Running data capture at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    generate(image_path)
