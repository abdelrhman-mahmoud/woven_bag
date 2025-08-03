import mysql.connector

def get_db_connection():
    """Establishes and returns a database connection."""
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="#ahlawy#bod@74#",
            database="control_panel_db"
        )
        return conn
    except mysql.connector.Error as err:
        if err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
            # Database doesn't exist, connect without specifying the DB
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="#ahlawy#bod@74#"
            )
            return conn
        else:
            raise

def initialize_database():
    """Creates the database if it doesn't exist."""
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="#ahlawy#bod@74#"
    )
    with conn.cursor() as c:
        c.execute("CREATE DATABASE IF NOT EXISTS control_panel_db")
    conn.close()

def create_tables():
    """Creates all tables if they don't exist."""
    conn = get_db_connection()
    with conn.cursor() as c:
        c.execute("USE control_panel_db")
        # Table for main_control_panel_processor
        c.execute('''CREATE TABLE IF NOT EXISTS control_panel1 (
            id INT PRIMARY KEY AUTO_INCREMENT,
            CurrentDateTime TEXT,
            HDPE_factor REAL,
            PP_factor REAL,
            HDPE_Exponent REAL,
            PP_Exponent REAL,
            HDPE_OutputFactorMeltPump REAL,
            PP_OutputFactorMeltPump REAL,
            Titer_g_9000m REAL,
            NumberOfTapes INTEGER,
            EdgeTrimSide_mm REAL,
            TapeWidth_mm REAL,
            CuttingWidth_mm REAL,
            TotalRatioTheoretical REAL,
            TotalRatioActual REAL,
            StretchRatioActual REAL,
            CalculatedPumpRPM REAL,
            RawMaterialPercentage REAL,
            AdditivePercentage TEXT,
            Company TEXT,
            ExtruderType TEXT,
            ScrewType TEXT,
            DieType TEXT,
            AlarmMessages TEXT
        )''')
        # Table for temperature_and_motor_data_processor
        c.execute('''CREATE TABLE IF NOT EXISTS control_panel2 (
            id INT PRIMARY KEY AUTO_INCREMENT,
            CurrentDateTime TEXT,
            OIL_HEATER_Target_Temp_1 REAL,
            OIL_HEATER_Actual_Temp_1 REAL,
            OIL_HEATER_Target_Temp_2 REAL,
            OIL_HEATER_Actual_Temp_2 REAL,
            HOT_AIR_Target_Temp REAL,
            HOT_AIR_Actual_Temp REAL,
            ANNEALING_Percentage REAL,
            Line_Speed_1 REAL,
            Amperage_1 REAL,
            Torque_1 REAL,
            Line_Speed_2 REAL,
            Amperage_2 REAL,
            Torque_2 REAL,
            Line_Speed_3 REAL,
            Amperage_3 REAL,
            Torque_3 REAL,
            AlarmMessages TEXT
        )''')
        # Table for extrusion_line_overview_processor
        c.execute('''CREATE TABLE IF NOT EXISTS control_panel3 (
            id INT PRIMARY KEY AUTO_INCREMENT,
            CurrentDateTime TEXT,
            LineSpeed_rpm REAL,
            CutTension_kg REAL,
            ExtruderSpeed_rpm REAL,
            TakeOffSpeed_mpm REAL,
            FilmOscillation_mm REAL,
            WaterExhaust_status TEXT,
            WaterPump_status TEXT,
            AlarmMessages TEXT
        )''')
        # Table for godet_and_extruder_data_processor
        c.execute('''CREATE TABLE IF NOT EXISTS control_panel4 (
            id INT PRIMARY KEY AUTO_INCREMENT,
            CurrentDateTime TEXT,
            OilHeater1_Temp_C REAL,
            OilHeater2_Temp_C REAL,
            TotalRatio REAL,
            StretchRatio REAL,
            Annealing_percent TEXT,
            Godet1_speed_ms REAL,
            Godet1_temp_C REAL,
            Godet2_speed_mpm REAL,
            Godet2_current_A REAL,
            Godet3_speed_mpm REAL,
            Godet3_current_A REAL,
            Godet4_speed_mpm REAL,
            Godet4_current_A REAL,
            Godet4_torque_percent REAL,
            Extruder_speed_rpm REAL,
            Zone1_temp_C REAL,
            Zone1_pressure REAL,
            Zone1_motor_load_percent REAL,
            Zone2_temp_C REAL,
            Zone2_pressure REAL,
            Zone2_motor_load_percent REAL,
            Zone2_torque_percent REAL,
            AlarmMessages TEXT
        )''')
        # Table for main_control_panel_alarm_processor
        c.execute('''CREATE TABLE IF NOT EXISTS control_panel5 (
            id INT PRIMARY KEY AUTO_INCREMENT,
            CurrentDateTime TEXT,
            LineSpeed_rpm REAL,
            CutTension_kg REAL,
            ExtruderSpeed_rpm REAL,
            TakeOffSpeed_mpm REAL,
            FilmOscillation_mm REAL,
            WaterExhaust_status TEXT,
            WaterPump_status TEXT,
            Extruder_status TEXT,
            AlarmMessages TEXT
        )''')
        # Table for extruder_details_processor
        c.execute('''CREATE TABLE IF NOT EXISTS control_panel6 (
            id INT PRIMARY KEY AUTO_INCREMENT,
            CurrentDateTime TEXT,
            LineSpeed_m_min REAL,
            Output_kg REAL,
            Extruder_rpm REAL,
            Extruder_Nm REAL,
            Z1_temp REAL,
            Z2_temp REAL,
            Z3_temp REAL,
            Z4_temp REAL,
            Z5_temp REAL,
            Z6_temp REAL,
            Z11_temp REAL,
            Z13_temp REAL,
            Z14_temp REAL,
            AlarmMessages TEXT
        )''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    initialize_database()
    create_tables()
    print("Database and tables initialized successfully.")
