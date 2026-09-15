import sqlite3
import os

# SQLite database file path
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

SAMPLE_PRINTERS = [
    {
        "Printer Name": "ES-CAR-PRT-001",
        "YSoft SafeQ 6 Site Server": "srv-safeq-es01.sabic.corp",
        "Business Critical": "Yes",
        "Turnaround": "Q3-2026",
        "Spare?": "No",
        "Business (ETP, EP, SHPP)": "ETP",
        "Status": "Active",
        "MACD / Orderdesk info (in progress)": "None",
        "Model": "Xerox AltaLink C8170",
        "Location": "Central Building - 1st Floor",
        "City": "Cartagena",
        "Site": "Cartagena Site",
        "Street Address": "Ctra. La Aljorra s/n",
        "Postal Code": "30390",
        "Country": "Spain",
        "Serial Number": "XRX-CART-9901",
        "Asset Tag": "AT-ES-0841",
        "IP Address": "10.42.12.14",
        "Subnet Mask": "255.255.255.0",
        "MAC Address": "00:00:AA:12:34:56",
        "SAP Queues": "CAR_ETP_01, CAR_SEC_01",
        "Install Date": "2022-03-15",
        "Lease exp.": "2027-03-15",
        "Infoblox address reservation + A/PTR Record": "Yes - Reserved",
        "Firmware": "103.004.015",
        "SABIC pwd": "Yes",
        "IP by / or USB": "Network IP",
        "YSoft Auth. Method": "Badge (MIFARE)",
        "Copy released (YSoft 'To each application')": "Enabled",
        "Activity code": "ACT-771",
        "Remarks": "Main reception multifunction printer",
        "Extra Remark": "Black toner replacement completed",
        "Actions done": "Hardening and admin password verified"
    },
    {
        "Printer Name": "ES-CAR-SPARE-001",
        "YSoft SafeQ 6 Site Server": "srv-safeq-es01.sabic.corp",
        "Business Critical": "No",
        "Turnaround": "Standby",
        "Spare?": "Yes",
        "Business (ETP, EP, SHPP)": "EP",
        "Status": "Offline",
        "MACD / Orderdesk info (in progress)": "Ticket #44892 (Assign to QC Lab)",
        "Model": "Xerox VersaLink C405",
        "Location": "IT Storage - Shelf B",
        "City": "Cartagena",
        "Site": "Cartagena Site",
        "Street Address": "Ctra. La Aljorra s/n",
        "Postal Code": "30390",
        "Country": "Spain",
        "Serial Number": "XRX-CART-SP01",
        "Asset Tag": "AT-ES-0992",
        "IP Address": "10.42.12.250",
        "Subnet Mask": "255.255.255.0",
        "MAC Address": "00:00:AA:12:34:99",
        "SAP Queues": "None",
        "Install Date": "2023-01-10",
        "Lease exp.": "2028-01-10",
        "Infoblox address reservation + A/PTR Record": "Yes - Reserved",
        "Firmware": "101.002.008",
        "SABIC pwd": "Yes",
        "IP by / or USB": "Network IP",
        "YSoft Auth. Method": "PIN / Badge",
        "Copy released (YSoft 'To each application')": "Disabled",
        "Activity code": "ACT-IT-RES",
        "Remarks": "Emergency spare printer for fast replacement",
        "Extra Remark": "Tested and boxed",
        "Actions done": "Reset and configured ready for deployment"
    },
    {
        "Printer Name": "NL-BOZ-PRT-004",
        "YSoft SafeQ 6 Site Server": "srv-safeq-nl01.sabic.corp",
        "Business Critical": "Yes",
        "Turnaround": "Q4-2026",
        "Spare?": "No",
        "Business (ETP, EP, SHPP)": "SHPP",
        "Status": "Active",
        "MACD / Orderdesk info (in progress)": "None",
        "Model": "Xerox AltaLink C8070",
        "Location": "Building 14 - Control Room",
        "City": "Bergen op Zoom",
        "Site": "Bergen op Zoom Site",
        "Street Address": "Plasticslaan 1",
        "Postal Code": "4612 PX",
        "Country": "Netherlands",
        "Serial Number": "XRX-BOZ-4412",
        "Asset Tag": "AT-NL-1209",
        "IP Address": "10.50.8.44",
        "Subnet Mask": "255.255.255.0",
        "MAC Address": "00:00:BB:45:67:89",
        "SAP Queues": "BOZ_SHPP_P1",
        "Install Date": "2021-06-20",
        "Lease exp.": "2026-06-20",
        "Infoblox address reservation + A/PTR Record": "Yes - Reserved",
        "Firmware": "103.001.045",
        "SABIC pwd": "No",
        "IP by / or USB": "Network IP",
        "YSoft Auth. Method": "Badge (HID Prox)",
        "Copy released (YSoft 'To each application')": "Enabled",
        "Activity code": "ACT-882",
        "Remarks": "Admin password update pending (audit non-compliant)",
        "Extra Remark": "Local desktop team notified",
        "Actions done": "Scheduled for remote hardening update"
    },
    {
        "Printer Name": "NL-GEL-OLD-001",
        "YSoft SafeQ 6 Site Server": "srv-safeq-nl02.sabic.corp",
        "Business Critical": "No",
        "Turnaround": "Decommissioned",
        "Spare?": "No",
        "Business (ETP, EP, SHPP)": "ETP",
        "Status": "DISPOSED",
        "MACD / Orderdesk info (in progress)": "Recycled by Xerox partner",
        "Model": "Xerox WorkCentre 5855",
        "Location": "Recycling Bay 3",
        "City": "Geleen",
        "Site": "Geleen Site",
        "Street Address": "Urmonderbaan 22",
        "Postal Code": "6167 RD",
        "Country": "Netherlands",
        "Serial Number": "XRX-GEL-OLD88",
        "Asset Tag": "AT-NL-1002",
        "IP Address": "10.60.4.99",
        "Subnet Mask": "255.255.255.0",
        "MAC Address": "00:00:CC:00:11:22",
        "SAP Queues": "None",
        "Install Date": "2018-05-10",
        "Lease exp.": "2023-05-10",
        "Infoblox address reservation + A/PTR Record": "Released / Deleted",
        "Firmware": "073.040.075",
        "SABIC pwd": "Yes",
        "IP by / or USB": "Network IP",
        "YSoft Auth. Method": "None",
        "Copy released (YSoft 'To each application')": "Disabled",
        "Activity code": "ACT-DISP",
        "Remarks": "End of life device - securely wiped and disposed",
        "Extra Remark": "Certificate of destruction received",
        "Actions done": "Hard drive shredded and removed from asset ledger"
    }
]

def build_database():
    """Initializes the SQLite database schema and inserts sample records."""
    conn = sqlite3.connect(DB_FILENAME)
    cursor = conn.cursor()

    col_defs = ['"Serial Number" TEXT PRIMARY KEY']
    for col in ALL_33_COLUMNS:
        if col != "Serial Number":
            col_defs.append(f'"{col}" TEXT')

    create_table_sql = f"CREATE TABLE IF NOT EXISTS printers ({', '.join(col_defs)});"
    cursor.execute(create_table_sql)

    for item in SAMPLE_PRINTERS:
        columns = [f'"{k}"' for k in item.keys()]
        placeholders = [":" + k for k in item.keys()]
        update_clause = [f'"{k}" = excluded."{k}"' for k in item.keys() if k != "Serial Number"]

        upsert_sql = f"""
        INSERT INTO printers ({', '.join(columns)})
        VALUES ({', '.join(placeholders)})
        ON CONFLICT("Serial Number") DO UPDATE SET
        {', '.join(update_clause)};
        """
        cursor.execute(upsert_sql, item)

    conn.commit()
    conn.close()
    print(f"[OK] Database successfully created at: {os.path.abspath(DB_FILENAME)}")

if __name__ == "__main__":
    build_database()