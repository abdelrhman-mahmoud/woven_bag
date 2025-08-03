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
        password="#ahlawy#bod@74#"
    )
    with conn.cursor() as c:
        c.execute("CREATE DATABASE IF NOT EXISTS control_panel_db")
        c.execute("USE control_panel_db")
        c.execute("DROP TABLE IF EXISTS control_panel7")
        c.execute('''CREATE TABLE IF NOT EXISTS control_panel7 (
            id INT PRIMARY KEY AUTO_INCREMENT,
            CurrentDateTime TEXT,
            Voltmeter_V REAL,
            Ammeter_A REAL,
            RedLight_status TEXT,
            YellowLight_status TEXT,
            BlueLight_status TEXT
        )''')
    conn.commit()
    return conn

def insert_data(conn, data):
    with conn.cursor() as c:
        c.execute('''INSERT INTO control_panel7 (CurrentDateTime, Voltmeter_V, Ammeter_A, RedLight_status, YellowLight_status, BlueLight_status)
                     VALUES (%s, %s, %s, %s, %s, %s)''',
                  (data.CurrentDateTime, data.Voltmeter_V, data.Ammeter_A, data.RedLight_status, data.YellowLight_status, data.BlueLight_status))
    conn.commit()

prompt = """Analyze the provided control panel image. The image shows a simple control panel with two analog meters and three indicator lights. Extract the following specific fields:

* CurrentDateTime: The date and time the image was taken, which is provided in the image metadata.
* Voltmeter_V: The reading on the voltmeter in volts (V).
* Ammeter_A: The reading on the ammeter in amperes (A).
* RedLight_status: The status of the red indicator light (ON/OFF).
* YellowLight_status: The status of the yellow indicator light (ON/OFF).
* BlueLight_status: The status of the blue indicator light (ON/OFF).

Return the data strictly as a JSON object with a single 'items' key containing a list of objects. Ensure all numeric values are numbers (not strings) and exclude units from the JSON values themselves, relying on the field descriptions for context. For any requested numeric measure that is not explicitly visible or clearly identifiable on the screen, return `null`. Do not include any additional text or explanations outside the JSON object.
"""

class ControlPanelData(BaseModel):
    CurrentDateTime: str = Field(..., description="The date and time the image was taken.")
    Voltmeter_V: Optional[float] = Field(None, description="The reading on the voltmeter in volts (V).")
    Ammeter_A: Optional[float] = Field(None, description="The reading on the ammeter in amperes (A).")
    RedLight_status: Optional[str] = Field(None, description="The status of the red indicator light (ON/OFF).")
    YellowLight_status: Optional[str] = Field(None, description="The status of the yellow indicator light (ON/OFF).")
    BlueLight_status: Optional[str] = Field(None, description="The status of the blue indicator light (ON/OFF).")

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
    image_path = r"images/7.jpg"
    print(f"Running data capture at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    generate(image_path)
