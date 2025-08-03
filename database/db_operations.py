import json
from .db_setup import get_db_connection

def insert_control_panel1_data(data):
    conn = get_db_connection()
    with conn.cursor() as c:
        c.execute('''INSERT INTO control_panel1 (CurrentDateTime, HDPE_factor, PP_factor, HDPE_Exponent, PP_Exponent,
                     HDPE_OutputFactorMeltPump, PP_OutputFactorMeltPump, Titer_g_9000m, NumberOfTapes, EdgeTrimSide_mm,
                     TapeWidth_mm, CuttingWidth_mm, TotalRatioTheoretical, TotalRatioActual, StretchRatioActual,
                     CalculatedPumpRPM, RawMaterialPercentage, AdditivePercentage, Company, ExtruderType, ScrewType,
                     DieType, AlarmMessages)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                  (data.CurrentDateTime, data.HDPE_factor, data.PP_factor, data.HDPE_Exponent, data.PP_Exponent,
                   data.HDPE_OutputFactorMeltPump, data.PP_OutputFactorMeltPump, data.Titer_g_9000m, data.NumberOfTapes,
                   data.EdgeTrimSide_mm, data.TapeWidth_mm, data.CuttingWidth_mm, data.TotalRatioTheoretical,
                   data.TotalRatioActual, data.StretchRatioActual, data.CalculatedPumpRPM, data.RawMaterialPercentage,
                   json.dumps(data.AdditivePercentage), data.Company, data.ExtruderType, data.ScrewType, data.DieType,
                   json.dumps(data.AlarmMessages)))
    conn.commit()
    conn.close()

def insert_control_panel2_data(data):
    conn = get_db_connection()
    with conn.cursor() as c:
        c.execute('''INSERT INTO control_panel2 (CurrentDateTime, OIL_HEATER_Target_Temp_1, OIL_HEATER_Actual_Temp_1,
                    OIL_HEATER_Target_Temp_2, OIL_HEATER_Actual_Temp_2, HOT_AIR_Target_Temp, HOT_AIR_Actual_Temp,
                    ANNEALING_Percentage, Line_Speed_1, Amperage_1, Torque_1, Line_Speed_2, Amperage_2, Torque_2,
                    Line_Speed_3, Amperage_3, Torque_3, AlarmMessages)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                  (data.CurrentDateTime, data.OIL_HEATER_Target_Temp_1, data.OIL_HEATER_Actual_Temp_1,
                   data.OIL_HEATER_Target_Temp_2, data.OIL_HEATER_Actual_Temp_2, data.HOT_AIR_Target_Temp,
                   data.HOT_AIR_Actual_Temp, data.ANNEALING_Percentage, data.Line_Speed_1, data.Amperage_1,
                   data.Torque_1, data.Line_Speed_2, data.Amperage_2, data.Torque_2, data.Line_Speed_3,
                   data.Amperage_3, data.Torque_3, json.dumps(data.AlarmMessages)))
    conn.commit()
    conn.close()

def insert_control_panel3_data(data):
    conn = get_db_connection()
    with conn.cursor() as c:
        c.execute('''INSERT INTO control_panel3 (CurrentDateTime, LineSpeed_rpm, CutTension_kg, ExtruderSpeed_rpm, TakeOffSpeed_mpm, FilmOscillation_mm, WaterExhaust_status, WaterPump_status, AlarmMessages)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                  (data.CurrentDateTime, data.LineSpeed_rpm, data.CutTension_kg, data.ExtruderSpeed_rpm, data.TakeOffSpeed_mpm, data.FilmOscillation_mm, data.WaterExhaust_status, data.WaterPump_status, json.dumps(data.AlarmMessages)))
    conn.commit()
    conn.close()

def insert_control_panel4_data(data):
    conn = get_db_connection()
    with conn.cursor() as c:
        c.execute('''INSERT INTO control_panel4 (CurrentDateTime, OilHeater1_Temp_C, OilHeater2_Temp_C, TotalRatio, StretchRatio, Annealing_percent, Godet1_speed_ms, Godet1_temp_C, Godet2_speed_mpm, Godet2_current_A, Godet3_speed_mpm, Godet3_current_A, Godet4_speed_mpm, Godet4_current_A, Godet4_torque_percent, Extruder_speed_rpm, Zone1_temp_C, Zone1_pressure, Zone1_motor_load_percent, Zone2_temp_C, Zone2_pressure, Zone2_motor_load_percent, Zone2_torque_percent, AlarmMessages)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                  (data.CurrentDateTime, data.OilHeater1_Temp_C, data.OilHeater2_Temp_C, data.TotalRatio, data.StretchRatio, data.Annealing_percent, data.Godet1_speed_ms, data.Godet1_temp_C, data.Godet2_speed_mpm, data.Godet2_current_A, data.Godet3_speed_mpm, data.Godet3_current_A, data.Godet4_speed_mpm, data.Godet4_current_A, data.Godet4_torque_percent, data.Extruder_speed_rpm, data.Zone1_temp_C, data.Zone1_pressure, data.Zone1_motor_load_percent, data.Zone2_temp_C, data.Zone2_pressure, data.Zone2_motor_load_percent, data.Zone2_torque_percent, json.dumps(data.AlarmMessages)))

def insert_control_panel5_data(data):
    conn = get_db_connection()
    with conn.cursor() as c:
        c.execute('''INSERT INTO control_panel5 (
            CurrentDateTime, LineSpeed_rpm, CutTension_kg, ExtruderSpeed_rpm,
            TakeOffSpeed_mpm, FilmOscillation_mm, WaterExhaust_status,
            WaterPump_status, Extruder_status, AlarmMessages
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
        (
            data.CurrentDateTime, data.LineSpeed_rpm, data.CutTension_kg,
            data.ExtruderSpeed_rpm, data.TakeOffSpeed_mpm, data.FilmOscillation_mm,
            data.WaterExhaust_status, data.WaterPump_status, data.Extruder_status,
            json.dumps(data.AlarmMessages)
        ))
    conn.commit()
    conn.close()

def insert_control_panel6_data(data):
    conn = get_db_connection()
    with conn.cursor() as c:
        c.execute('''INSERT INTO control_panel6 (CurrentDateTime, LineSpeed_m_min, Output_kg, Extruder_rpm, Extruder_Nm, Z1_temp, Z2_temp, Z3_temp, Z4_temp, Z5_temp, Z6_temp, Z11_temp, Z13_temp, Z14_temp, AlarmMessages)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,. %s, %s, %s)''',
                  (data.CurrentDateTime, data.LineSpeed_m_min, data.Output_kg, data.Extruder_rpm, data.Extruder_Nm, data.Z1_temp, data.Z2_temp, data.Z3_temp, data.Z4_temp, data.Z5_temp, data.Z6_temp, data.Z11_temp, data.Z13_temp, data.Z14_temp, json.dumps(data.AlarmMessages)))
    conn.commit()
    conn.close()
