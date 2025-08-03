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
        c.execute("DROP TABLE IF EXISTS control_panel10")
        c.execute('''CREATE TABLE IF NOT EXISTS control_panel10 (
            id INT PRIMARY KEY AUTO_INCREMENT,
            CurrentDateTime TEXT,
            Run_status TEXT,
            Run_value REAL,
            P_per_10cm REAL,
            Speed_m_min REAL,
            Shift REAL,
            Efficiency_percent REAL,
            Total_m2 REAL,
            Total_m REAL,
            Value_300 REAL,
            Value_150_g_1 REAL,
            Value_150_g_2 REAL,
            Value_432_4 REAL,
            Value_118_kg REAL
        )''')
    conn.commit()
    return conn

def insert_data(conn, data):
    with conn.cursor() as c:
        c.execute('''INSERT INTO control_panel10 (CurrentDateTime, Run_status, Run_value, P_per_10cm, Speed_m_min, Shift, Efficiency_percent, Total_m2, Total_m, Value_300, Value_150_g_1, Value_150_g_2, Value_432_4, Value_118_kg)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                  (data.CurrentDateTime, data.Run_status, data.Run_value, data.P_per_10cm, data.Speed_m_min, data.Shift, data.Efficiency_percent, data.Total_m2, data.Total_m, data.Value_300, data.Value_150_g_1, data.Value_150_g_2, data.Value_432_4, data.Value_118_kg))
    conn.commit()

prompt = """Analyze the provided control panel image from a BSW intelliCon machine. Extract the following specific fields:

* CurrentDateTime: The date and time displayed on the screen (e.g., "DD.MM.YYYY HH:MM:SS").
* Run_status: The status of the machine (e.g., RUN).
* Run_value: The numeric value associated with the RUN status.
* P_per_10cm: The value for P/10cm.
* Speed_m_min: The speed in m/min.
* Shift: The current shift number.
* Efficiency_percent: The efficiency in %.
* Total_m2: The total area in m2.
* Total_m: The total length in m.
* Value_300: The value '300' displayed on the screen.
* Value_150_g_1: The first value '150 g' displayed on the screen.
* Value_150_g_2: The second value '150 g' displayed on the screen.
* Value_432_4: The value '432.4' displayed on the screen.
* Value_118_kg: The value '118 kg' displayed on the screen.

Return the data strictly as a JSON object with a single 'items' key containing a list of objects. Ensure all numeric values are numbers (not strings) and exclude units from the JSON values themselves, relying on the field descriptions for context. For any requested numeric measure that is not explicitly visible or clearly identifiable on the screen, return `null`. Do not include any additional text or explanations outside the JSON object.
"""

class ControlPanelData(BaseModel):
    CurrentDateTime: str = Field(..., description="The date and time displayed on the screen.")
    Run_status: Optional[str] = Field(None, description="The status of the machine (e.g., RUN).")
    Run_value: Optional[float] = Field(None, description="The numeric value associated with the RUN status.")
    P_per_10cm: Optional[float] = Field(None, description="The value for P/10cm.")
    Speed_m_min: Optional[float] = Field(None, description="The speed in m/min.")
    Shift: Optional[int] = Field(None, description="The current shift number.")
    Efficiency_percent: Optional[float] = Field(None, description="The efficiency in %.")
    Total_m2: Optional[float] = Field(None, description="The total area in m2.")
    Total_m: Optional[float] = Field(None, description="The total length in m.")
    Value_300: Optional[int] = Field(None, description="The value '300' displayed on the screen.")
    Value_150_g_1: Optional[int] = Field(None, description="The first value '150 g' displayed on the screen.")
    Value_150_g_2: Optional[int] = Field(None, description="The second value '150 g' displayed on the screen.")
    Value_432_4: Optional[float] = Field(None, description="The value '432.4' displayed on the screen.")
    Value_118_kg: Optional[int] = Field(None, description="The value '118 kg' displayed on the screen.")

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
    image_path = r"images/10.jpg"
    print(f"Running data capture at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    generate(image_path)
