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
        c.execute("DROP TABLE IF EXISTS control_panel9")
        c.execute('''CREATE TABLE IF NOT EXISTS control_panel9 (
            id INT PRIMARY KEY AUTO_INCREMENT,
            CurrentDateTime TEXT,
            ACT1_kg REAL,
            ACT2_kg REAL,
            Fabric_Mtr REAL,
            Efficiency_percent REAL,
            MainSwitchTime_Hrs TEXT,
            OperatingTime_Hrs TEXT,
            WarpBreak REAL,
            WeftBreak REAL,
            WeftEnd REAL,
            Tapes_per_10cm REAL,
            Picks_per_Min REAL
        )''')
    conn.commit()
    return conn

def insert_data(conn, data):
    with conn.cursor() as c:
        c.execute('''INSERT INTO control_panel9 (CurrentDateTime, ACT1_kg, ACT2_kg, Fabric_Mtr, Efficiency_percent, MainSwitchTime_Hrs, OperatingTime_Hrs, WarpBreak, WeftBreak, WeftEnd, Tapes_per_10cm, Picks_per_Min)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                  (data.CurrentDateTime, data.ACT1_kg, data.ACT2_kg, data.Fabric_Mtr, data.Efficiency_percent, data.MainSwitchTime_Hrs, data.OperatingTime_Hrs, data.WarpBreak, data.WeftBreak, data.WeftEnd, data.Tapes_per_10cm, data.Picks_per_Min))
    conn.commit()

prompt = """Analyze the provided control panel image from a Lohia Corp machine. Extract the following specific fields:

* CurrentDateTime: The date and time the image was taken, which is provided in the image metadata.
* ACT1_kg: The value for ACT1 in kg.
* ACT2_kg: The value for ACT2 in kg.
* Fabric_Mtr: The value for Fabric in Mtr.
* Efficiency_percent: The value for Efficiency in %.
* MainSwitchTime_Hrs: The value for Main Switch Time in Hrs.
* OperatingTime_Hrs: The value for Operating Time in Hrs.
* WarpBreak: The value for Warp Break.
* WeftBreak: The value for Weft Break.
* WeftEnd: The value for Weft End.
* Tapes_per_10cm: The value for Tapes/10cm.
* Picks_per_Min: The value for Picks/Min.

Return the data strictly as a JSON object with a single 'items' key containing a list of objects. Ensure all numeric values are numbers (not strings) and exclude units from the JSON values themselves, relying on the field descriptions for context. For any requested numeric measure that is not explicitly visible or clearly identifiable on the screen, return `null`. Do not include any additional text or explanations outside the JSON object.
"""

class ControlPanelData(BaseModel):
    CurrentDateTime: str = Field(..., description="The date and time the image was taken.")
    ACT1_kg: Optional[float] = Field(None, description="The value for ACT1 in kg.")
    ACT2_kg: Optional[float] = Field(None, description="The value for ACT2 in kg.")
    Fabric_Mtr: Optional[float] = Field(None, description="The value for Fabric in Mtr.")
    Efficiency_percent: Optional[float] = Field(None, description="The value for Efficiency in %.")
    MainSwitchTime_Hrs: Optional[str] = Field(None, description="The value for Main Switch Time in Hrs.")
    OperatingTime_Hrs: Optional[str] = Field(None, description="The value for Operating Time in Hrs.")
    WarpBreak: Optional[int] = Field(None, description="The value for Warp Break.")
    WeftBreak: Optional[int] = Field(None, description="The value for Weft Break.")
    WeftEnd: Optional[int] = Field(None, description="The value for Weft End.")
    Tapes_per_10cm: Optional[float] = Field(None, description="The value for Tapes/10cm.")
    Picks_per_Min: Optional[int] = Field(None, description="The value for Picks/Min.")

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
    image_path = r"images/9.jpg"
    print(f"Running data capture at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    generate(image_path)
