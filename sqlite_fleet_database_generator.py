import sqlite3
import os
import random
from datetime import datetime, timedelta

DB_FILENAME = "flota_impresoras.db"

ALL_33_COLUMNS = [
    "Printer Name",
    "YSoft SafeQ 6 Site Server",
    "Business Critical",
    "Turnaround",
    "Spare?",
    "Business (ETP, EP, SHPP)",
    "Status",
    "MACD / Orderdesk info (in progress)",
    "Model",
    "Location",
    "City",
    "Site",
    "Street Address",
    "Postal Code",
    "Country",
    "Serial Number",
    "Asset Tag",
    "IP Address",
    "Subnet Mask",
    "MAC Address",
    "SAP Queues",
    "Install Date",
    "Lease exp.",
    "Infoblox address reservation + A/PTR Record",
    "Firmware",
    "SABIC pwd",
    "IP by / or USB",
    "YSoft Auth. Method",
    "Copy released (YSoft 'To each application')",
    "Activity code",
    "Remarks",
    "Extra Remark",
    "Actions done"
]

SITES_DATA = [
    {
        "site": "Cartagena Site",
        "city": "Cartagena",
        "country": "Spain",
        "prefix": "ES-CAR",
        "street": "Ctra. La Aljorra s/n",
        "zip": "30390",
        "subnet": "10.42",
        "ysoft": "srv-safeq-es01.sabic.corp"
    },
    {
        "site": "Bergen op Zoom Site",
        "city": "Bergen op Zoom",
        "country": "Netherlands",
        "prefix": "NL-BOZ",
        "street": "Plasticslaan 1",
        "zip": "4612 PX",
        "subnet": "10.50",
        "ysoft": "srv-safeq-nl01.sabic.corp"
    },
    {
        "site": "Geleen Site",
        "city": "Geleen",
        "country": "Netherlands",
        "prefix": "NL-GEL",
        "street": "Urmonderbaan 22",
        "zip": "6167 RD",
        "subnet": "10.60",
        "ysoft": "srv-safeq-nl02.sabic.corp"
    },
    {
        "site": "Teesside Wilton Site",
        "city": "Wilton",
        "country": "United Kingdom",
        "prefix": "UK-TSD",
        "street": "Wilton International",
        "zip": "TS10 4RF",
        "subnet": "10.72",
        "ysoft": "srv-safeq-uk01.sabic.corp"
    }
]

MODELS = [
    ("Xerox AltaLink C8170", "MFD Color A3"),
    ("Xerox AltaLink C8055", "MFD Color A3"),
    ("Xerox VersaLink C405", "MFD Color A4"),
    ("Xerox VersaLink B405", "MFD Mono A4"),
    ("Xerox WorkCentre 5855", "MFD Mono A3 - Legacy")
]

BUSINESS_UNITS = ["ETP", "EP", "SHPP"]
BUILDINGS = ["Central Admin", "QC Lab", "Warehouse Bay 3", "Production Unit 1", "Engineering Plant", "Logistics Gate", "R&D Center", "Safety Department"]
AUTH_METHODS = ["Badge (MIFARE)", "Badge (HID Prox)", "PIN / Badge", "PIN Only"]
FIRMWARES = ["103.004.015", "103.001.045", "101.002.008", "104.002.019", "073.040.075"]

def generate_50_printers():
    printers = []
    # Seed fixed for consistency but realistic distribution
    random.seed(42)

    for i in range(1, 51):
        site_info = SITES_DATA[i % len(SITES_DATA)]
        model_name, _ = random.choice(MODELS)
        bu = random.choice(BUSINESS_UNITS)
        building = random.choice(BUILDINGS)
        floor = random.choice(["Ground Floor", "1st Floor", "2nd Floor", "Control Room"])
        
        # Determine status and spare distribution
        is_spare = "Yes" if i in [5, 12, 24, 38, 49] else "No"
        
        if i in [18, 33]:
            status = "DISPOSED"
        elif i in [8, 27]:
            status = "Offline"
        elif i in [14, 42]:
            status = "Temp. Offline"
        else:
            status = "Active"

        # Hardening compliance (5 printers non-compliant for audit tests)
        sabic_pwd = "No" if i in [7, 19, 29, 36, 47] else "Yes"
        is_critical = "Yes" if (building in ["QC Lab", "Production Unit 1", "Logistics Gate"] and is_spare == "No") else "No"

        # Generate realistic dates
        install_year = random.choice([2021, 2022, 2023, 2024])
        install_date = f"{install_year}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
        lease_year = install_year + 5
        lease_exp = f"{lease_year}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"

        # Network details
        ip_oct4 = 10 + i
        ip_addr = f"{site_info['subnet']}.14.{ip_oct4}"
        mac_addr = f"00:00:AA:{random.randint(10, 99)}:{random.randint(10, 99)}:{i:02d}"
        serial_no = f"XRX-{site_info['prefix'][-3:]}-{8000 + i}"
        printer_code = f"SPARE-{i:03d}" if is_spare == "Yes" else f"PRT-{i:03d}"
        printer_name = f"{site_info['prefix']}-{printer_code}"
        asset_tag = f"AT-{site_info['prefix'][:2]}-{1000 + i}"
        sap_queue = f"{site_info['prefix'][-3:]}_{bu}_{i:02d}" if status != "DISPOSED" else "None"

        # MACD & Remarks
        macd_info = "None"
        if status == "DISPOSED":
            macd_info = "Disposal certificate archived"
        elif status == "Temp. Offline":
            macd_info = f"Ticket #{32000 + i}: Fuser replacement scheduled"
        elif is_spare == "Yes" and status == "Active":
            macd_info = "Standby ready in IT Storage"

        remarks = f"Assigned to {building}"
        if sabic_pwd == "No":
            extra_rem = "AUDIT ALERT: Default administrator credentials detected"
            actions_done = "Assigned ticket to site technician for urgent hardening"
        elif status == "DISPOSED":
            extra_rem = "Secure disk shredding complete"
            actions_done = "Decommissioned from SafeQ and Infoblox released"
        else:
            extra_rem = "Routine firmware update completed"
            actions_done = "SNMP & YSoft heartbeat verified"

        p_record = {
            "Printer Name": printer_name,
            "YSoft SafeQ 6 Site Server": site_info["ysoft"],
            "Business Critical": is_critical,
            "Turnaround": f"Q{random.randint(1,4)}-{lease_year}",
            "Spare?": is_spare,
            "Business (ETP, EP, SHPP)": bu,
            "Status": status,
            "MACD / Orderdesk info (in progress)": macd_info,
            "Model": model_name,
            "Location": f"{building} - {floor}",
            "City": site_info["city"],
            "Site": site_info["site"],
            "Street Address": site_info["street"],
            "Postal Code": site_info["zip"],
            "Country": site_info["country"],
            "Serial Number": serial_no,
            "Asset Tag": asset_tag,
            "IP Address": ip_addr,
            "Subnet Mask": "255.255.255.0",
            "MAC Address": mac_addr,
            "SAP Queues": sap_queue,
            "Install Date": install_date,
            "Lease exp.": lease_exp,
            "Infoblox address reservation + A/PTR Record": "Yes - Reserved" if status != "DISPOSED" else "Released / Deleted",
            "Firmware": random.choice(FIRMWARES),
            "SABIC pwd": sabic_pwd,
            "IP by / or USB": "Network IP",
            "YSoft Auth. Method": random.choice(AUTH_METHODS),
            "Copy released (YSoft 'To each application')": "Enabled" if status == "Active" else "Disabled",
            "Activity code": f"ACT-{bu}-{random.randint(100, 999)}",
            "Remarks": remarks,
            "Extra Remark": extra_rem,
            "Actions done": actions_done
        }
        printers.append(p_record)

    return printers

def build_database():
    """Initializes the SQLite database schema and inserts 50 synthetic test records."""
    conn = sqlite3.connect(DB_FILENAME)
    cursor = conn.cursor()

    col_defs = ['"Serial Number" TEXT PRIMARY KEY']
    for col in ALL_33_COLUMNS:
        if col != "Serial Number":
            col_defs.append(f'"{col}" TEXT')

    create_table_sql = f"CREATE TABLE IF NOT EXISTS printers ({', '.join(col_defs)});"
    cursor.execute(create_table_sql)

    dataset_50 = generate_50_printers()

    for item in dataset_50:
        keys = list(item.keys())
        columns = [f'"{k}"' for k in keys]
        placeholders = ['?'] * len(keys)
        values = [str(item[k]) if item[k] is not None else "" for k in keys]
        update_clause = [f'"{k}" = excluded."{k}"' for k in keys if k != "Serial Number"]

        upsert_sql = f"""
        INSERT INTO printers ({', '.join(columns)})
        VALUES ({', '.join(placeholders)})
        ON CONFLICT("Serial Number") DO UPDATE SET
        {', '.join(update_clause)};
        """
        cursor.execute(upsert_sql, values)

    conn.commit()
    conn.close()
    print(f"✅ Success! Created {len(dataset_50)} realistic European printers in: {os.path.abspath(DB_FILENAME)}")

if __name__ == "__main__":
    build_database()
