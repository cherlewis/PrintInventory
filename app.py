import sqlite3
import pandas as pd
import streamlit as st
from datetime import datetime
import io

st.set_page_config(
    page_title="PrintGuard EU - Xerox Fleet Management",
    page_icon="🖨️",
    layout="wide",
    initial_sidebar_state="expanded"
)

DB_NAME = "flota_impresoras.db"

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

STATUS_OPTIONS = ["Active", "DISPOSED", "Offline", "Temp. Offline"]
SPARE_OPTIONS = ["No", "Yes"]
SABIC_PWD_OPTIONS = ["Yes", "No"]
BUSINESS_CRITICAL_OPTIONS = ["No", "Yes"]

PRESETS = {
    "⭐ Basic View (4)": ["Printer Name", "Status", "Serial Number", "IP Address"],
    "🛡️ Hardening & Security": ["Printer Name", "Status", "IP Address", "Firmware", "SABIC pwd", "YSoft SafeQ 6 Site Server", "YSoft Auth. Method", "Business Critical"],
    "🌐 Network & Infoblox": ["Printer Name", "IP Address", "Subnet Mask", "MAC Address", "Infoblox address reservation + A/PTR Record", "Site", "Status"],
    "📄 SAP & Lifecycle": ["Printer Name", "SAP Queues", "MACD / Orderdesk info (in progress)", "Install Date", "Lease exp.", "Asset Tag", "Site"],
    "📑 Show All (33)": ALL_33_COLUMNS
}

def get_db_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    col_defs = ['"Serial Number" TEXT PRIMARY KEY']
    for col in ALL_33_COLUMNS:
        if col != "Serial Number":
            col_defs.append(f'"{col}" TEXT')
    cursor.execute(f"CREATE TABLE IF NOT EXISTS printers ({', '.join(col_defs)});")
    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM printers;")
    if cursor.fetchone()[0] == 0:
        seed_printers = [
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
            }
        ]
        for p in seed_printers:
            insert_or_update_printer(p)
    conn.close()

def get_all_printers_df():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM printers;", conn)
    conn.close()
    return df

def insert_or_update_printer(data_dict):
    conn = get_db_connection()
    cursor = conn.cursor()
    columns = [f'"{k}"' for k in data_dict.keys()]
    placeholders = [":" + k for k in data_dict.keys()]
    update_clause = [f'"{k}" = excluded."{k}"' for k in data_dict.keys() if k != "Serial Number"]
    sql = f"""
    INSERT INTO printers ({', '.join(columns)})
    VALUES ({', '.join(placeholders)})
    ON CONFLICT("Serial Number") DO UPDATE SET
    {', '.join(update_clause)};
    """
    cursor.execute(sql, data_dict)
    conn.commit()
    conn.close()

def delete_printer(serial_number):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM printers WHERE "Serial Number" = ?;', (serial_number,))
    conn.commit()
    conn.close()

init_db()

st.title("🖨️ PrintGuard EU — Xerox Fleet Management Console")
st.caption("European Multi-site Fleet Management, Security Audit & SQLite Database (33 Attributes)")

df_fleet = get_all_printers_df()
total_count = len(df_fleet)
active_count = len(df_fleet[df_fleet["Status"] == "Active"]) if total_count > 0 else 0
offline_count = len(df_fleet[df_fleet["Status"].isin(["Offline", "Temp. Offline"])]) if total_count > 0 else 0
spare_count = len(df_fleet[df_fleet["Spare?"] == "Yes"]) if total_count > 0 else 0
sabic_compliant_count = len(df_fleet[df_fleet["SABIC pwd"] == "Yes"]) if total_count > 0 else 0
sabic_rate = int((sabic_compliant_count / total_count * 100)) if total_count > 0 else 0

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Total Fleet", total_count, "Xerox EU")
m2.metric("Active / Online", active_count)
m3.metric("Offline / Alert", offline_count)
m4.metric("Spare Devices", spare_count, "Buffer")
m5.metric("SABIC Pwd Compliant", f"{sabic_rate}%", f"{total_count - sabic_compliant_count} non-compliant")

st.divider()

c_search, c_status, c_spare = st.columns([2, 1, 1])
with c_search:
    search_query = st.text_input("🔍 Global Search", placeholder="Filter by Name, IP, Serial, Model, Site...")
with c_status:
    status_filter = st.selectbox("Status Filter", ["ALL"] + STATUS_OPTIONS)
with c_spare:
    spare_filter = st.selectbox("Spare Filter", ["ALL", "Yes (Spares)", "No (Production)"])

st.write("**Quick Column Presets:**")
p_cols = st.columns(len(PRESETS))
for idx, (preset_name, cols) in enumerate(PRESETS.items()):
    if p_cols[idx].button(preset_name, use_container_width=True):
        st.session_state["active_cols"] = cols

if "active_cols" not in st.session_state:
    st.session_state["active_cols"] = PRESETS["⭐ Basic View (4)"]

chosen_columns = st.multiselect(
    "Custom Visible Columns:",
    options=ALL_33_COLUMNS,
    default=st.session_state["active_cols"]
)

filtered_df = df_fleet.copy()
if search_query:
    query_lower = search_query.lower()
    filtered_df = filtered_df[
        filtered_df.apply(lambda row: row.astype(str).str.lower().str.contains(query_lower).any(), axis=1)
    ]

if status_filter != "ALL":
    filtered_df = filtered_df[filtered_df["Status"] == status_filter]

if spare_filter == "Yes (Spares)":
    filtered_df = filtered_df[filtered_df["Spare?"] == "Yes"]
elif spare_filter == "No (Production)":
    filtered_df = filtered_df[filtered_df["Spare?"] == "No"]

st.subheader(f"Fleet Records ({len(filtered_df)} of {total_count})")
if len(chosen_columns) > 0:
    display_cols = [c for c in chosen_columns if c in filtered_df.columns]
    st.dataframe(filtered_df[display_cols], use_container_width=True, hide_index=True)

exp_col1, exp_col2 = st.columns([1, 1])
with exp_col1:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_fleet.to_excel(writer, sheet_name="Xerox_EU_Fleet", index=False)
    st.download_button(
        label="📥 Export Full 33-Column Excel",
        data=output.getvalue(),
        file_name=f"Xerox_EU_Fleet_{datetime.today().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

with exp_col2:
    with st.expander("📤 Import Fleet File (.xlsx / .csv) into SQLite"):
        uploaded_file = st.file_uploader("Upload inventory file:", type=["xlsx", "xls", "csv"])
        if uploaded_file is not None:
            if st.button("Apply Import to Database", type="primary"):
                imp_df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
                loaded = 0
                for _, row in imp_df.iterrows():
                    serial = str(row.get("Serial Number", row.get("Serial", row.get("N/S", "")))).strip()
                    if not serial or serial == "nan":
                        continue
                    row_dict = {}
                    for col in ALL_33_COLUMNS:
                        val = row.get(col, "")
                        row_dict[col] = "" if pd.isna(val) else str(val).strip()
                    row_dict["Serial Number"] = serial
                    if not row_dict.get("Status"): row_dict["Status"] = "Active"
                    if not row_dict.get("Spare?"): row_dict["Spare?"] = "No"
                    insert_or_update_printer(row_dict)
                    loaded += 1
                st.success(f"Successfully processed {loaded} printers!")
                st.rerun()

st.divider()

tab_edit, tab_new, tab_delete = st.tabs(["✏️ Edit Existing Device", "➕ Register New Device", "🗑️ Decommission / Delete"])

with tab_edit:
    st.write("### Edit Printer Attributes (33 Fields)")
    printer_choices = df_fleet["Serial Number"].tolist()
    if len(printer_choices) > 0:
        selected_sn = st.selectbox("Select Device by Serial Number:", printer_choices)
        selected_record = df_fleet[df_fleet["Serial Number"] == selected_sn].iloc[0].to_dict()

        with st.form("edit_printer_form"):
            t1, t2, t3, t4 = st.tabs(["1. Identity & Location", "2. Network & Infoblox", "3. Hardening & YSoft", "4. SAP & Lifecycle"])
            with t1:
                col_a, col_b, col_c = st.columns(3)
                p_name = col_a.text_input("Printer Name", value=selected_record.get("Printer Name", ""))
                p_status = col_b.selectbox("Status", STATUS_OPTIONS, index=STATUS_OPTIONS.index(selected_record.get("Status", "Active")) if selected_record.get("Status") in STATUS_OPTIONS else 0)
                p_spare = col_c.selectbox("Spare?", SPARE_OPTIONS, index=SPARE_OPTIONS.index(selected_record.get("Spare?", "No")) if selected_record.get("Spare?") in SPARE_OPTIONS else 0)
                
                col_d, col_e, col_f = st.columns(3)
                p_sn = col_d.text_input("Serial Number", value=selected_record.get("Serial Number", ""), disabled=True)
                p_model = col_e.text_input("Model", value=selected_record.get("Model", ""))
                p_crit = col_f.selectbox("Business Critical", BUSINESS_CRITICAL_OPTIONS, index=BUSINESS_CRITICAL_OPTIONS.index(selected_record.get("Business Critical", "No")) if selected_record.get("Business Critical") in BUSINESS_CRITICAL_OPTIONS else 0)

                col_g, col_h, col_i = st.columns(3)
                p_site = col_g.text_input("Site", value=selected_record.get("Site", ""))
                p_country = col_h.text_input("Country", value=selected_record.get("Country", ""))
                p_city = col_i.text_input("City", value=selected_record.get("City", ""))

                p_loc = st.text_input("Location", value=selected_record.get("Location", ""))
                p_street = st.text_input("Street Address", value=selected_record.get("Street Address", ""))
                p_post = st.text_input("Postal Code", value=selected_record.get("Postal Code", ""))

            with t2:
                col_n1, col_n2 = st.columns(2)
                p_ip = col_n1.text_input("IP Address", value=selected_record.get("IP Address", ""))
                p_sub = col_n2.text_input("Subnet Mask", value=selected_record.get("Subnet Mask", ""))
                col_n3, col_n4 = st.columns(2)
                p_mac = col_n3.text_input("MAC Address", value=selected_record.get("MAC Address", ""))
                p_ip_by = col_n4.text_input("IP by / or USB", value=selected_record.get("IP by / or USB", ""))
                p_infoblox = st.text_input("Infoblox reservation", value=selected_record.get("Infoblox address reservation + A/PTR Record", ""))

            with t3:
                col_h1, col_h2 = st.columns(2)
                p_sabic = col_h1.selectbox("SABIC pwd", SABIC_PWD_OPTIONS, index=SABIC_PWD_OPTIONS.index(selected_record.get("SABIC pwd", "Yes")) if selected_record.get("SABIC pwd") in SABIC_PWD_OPTIONS else 0)
                p_fw = col_h2.text_input("Firmware", value=selected_record.get("Firmware", ""))
                col_h3, col_h4 = st.columns(2)
                p_ysoft_srv = col_h3.text_input("YSoft Server", value=selected_record.get("YSoft SafeQ 6 Site Server", ""))
                p_ysoft_auth = col_h4.text_input("YSoft Auth", value=selected_record.get("YSoft Auth. Method", ""))
                p_copy = st.text_input("Copy released", value=selected_record.get("Copy released (YSoft 'To each application')", ""))

            with t4:
                col_l1, col_l2, col_l3 = st.columns(3)
                p_bu = col_l1.text_input("Business Unit", value=selected_record.get("Business (ETP, EP, SHPP)", ""))
                p_asset = col_l2.text_input("Asset Tag", value=selected_record.get("Asset Tag", ""))
                p_act = col_l3.text_input("Activity code", value=selected_record.get("Activity code", ""))
                p_sap = st.text_input("SAP Queues", value=selected_record.get("SAP Queues", ""))
                p_install = st.text_input("Install Date", value=selected_record.get("Install Date", ""))
                p_lease = st.text_input("Lease exp.", value=selected_record.get("Lease exp.", ""))
                p_turn = st.text_input("Turnaround", value=selected_record.get("Turnaround", ""))
                p_macd = st.text_input("MACD info", value=selected_record.get("MACD / Orderdesk info (in progress)", ""))
                p_rem = st.text_area("Remarks", value=selected_record.get("Remarks", ""))
                p_extra = st.text_area("Extra Remark", value=selected_record.get("Extra Remark", ""))
                p_actions = st.text_area("Actions done", value=selected_record.get("Actions done", ""))

            if st.form_submit_button("💾 Save Changes into SQLite", type="primary", use_container_width=True):
                updated_payload = {
                    "Printer Name": p_name, "YSoft SafeQ 6 Site Server": p_ysoft_srv, "Business Critical": p_crit,
                    "Turnaround": p_turn, "Spare?": p_spare, "Business (ETP, EP, SHPP)": p_bu, "Status": p_status,
                    "MACD / Orderdesk info (in progress)": p_macd, "Model": p_model, "Location": p_loc,
                    "City": p_city, "Site": p_site, "Street Address": p_street, "Postal Code": p_post,
                    "Country": p_country, "Serial Number": selected_sn, "Asset Tag": p_asset, "IP Address": p_ip,
                    "Subnet Mask": p_sub, "MAC Address": p_mac, "SAP Queues": p_sap, "Install Date": p_install,
                    "Lease exp.": p_lease, "Infoblox address reservation + A/PTR Record": p_infoblox,
                    "Firmware": p_fw, "SABIC pwd": p_sabic, "IP by / or USB": p_ip_by, "YSoft Auth. Method": p_ysoft_auth,
                    "Copy released (YSoft 'To each application')": p_copy, "Activity code": p_act,
                    "Remarks": p_rem, "Extra Remark": p_extra, "Actions done": p_actions
                }
                insert_or_update_printer(updated_payload)
                st.success(f"Device {p_name} updated!")
                st.rerun()

with tab_new:
    st.write("### Register New Device")
    with st.form("new_device_form"):
        col_n1, col_n2, col_n3 = st.columns(3)
        n_name = col_n1.text_input("Printer Name", value="NEW-PRT-01")
        n_sn = col_n2.text_input("Serial Number (Mandatory Key)", value="")
        n_ip = col_n3.text_input("IP Address", value="10.0.0.100")
        col_n4, col_n5 = st.columns(2)
        n_model = col_n4.text_input("Model", value="Xerox AltaLink C8170")
        n_site = col_n5.text_input("Site", value="Cartagena Site")
        if st.form_submit_button("✨ Create Device", type="primary", use_container_width=True):
            if not n_sn.strip():
                st.error("Serial Number is required.")
            else:
                p_data = {c: "" for c in ALL_33_COLUMNS}
                p_data.update({
                    "Printer Name": n_name, "Serial Number": n_sn.strip(),
                    "IP Address": n_ip, "Model": n_model, "Site": n_site,
                    "Status": "Active", "Spare?": "No", "SABIC pwd": "Yes"
                })
                insert_or_update_printer(p_data)
                st.success("Printer created!")
                st.rerun()

with tab_delete:
    st.write("### Decommission Device")
    if len(printer_choices) > 0:
        del_sn = st.selectbox("Select printer to delete:", printer_choices, key="del_box")
        confirm_chk = st.checkbox(f"Confirm permanent removal of {del_sn}")
        if st.button("🗑️ Delete from Database", type="primary", disabled=not confirm_chk):
            delete_printer(del_sn)
            st.success("Printer removed.")
            st.rerun()
