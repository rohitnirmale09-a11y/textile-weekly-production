import streamlit as st
import os
import pandas as pd
from datetime import date

# ----------------- CONSTANTS -----------------
TOTAL_MACHINES = 7
WASTAGE_PERCENT = 1.5
YARN_PER_METER = 0.02854

SUMMARY_FILE = "weekly_summary.csv"
MACHINE_FILE = "machine_stock.csv"
TODAY = date.today().isoformat()

# ----------------- APP CONFIG -----------------
st.set_page_config(page_title="SUDHIR TEXTILE", layout="wide")

st.title("🧵 SUDHIR TEXTILE")
st.write("मीटर, वेस्टेज व सूत साठा यांची व्यावसायिक गणना")

st.divider()

# ----------------- LOAD PREVIOUS DATA -----------------

# Load previous yarn stock
previous_yarn_stock_default = 0.0
if os.path.exists(SUMMARY_FILE):
    df_summary_old = pd.read_csv(SUMMARY_FILE)
    previous_yarn_stock_default = float(df_summary_old.iloc[-1]["remaining_yarn"])

# Load previous machine remaining stock
previous_machine_stock = {}
if os.path.exists(MACHINE_FILE):
    df_machine_old = pd.read_csv(MACHINE_FILE)
    last_date = df_machine_old["date"].iloc[-1]
    last_week_data = df_machine_old[df_machine_old["date"] == last_date]

    for _, row in last_week_data.iterrows():
        previous_machine_stock[int(row["machine"])] = float(row["remaining_taga"])

# ----------------- YARN STOCK INPUT -----------------
st.subheader("🧶 सूत साठा")

previous_yarn_stock = st.number_input(
    "मागील सूत साठा (kg)",
    value=previous_yarn_stock_default,
    min_value=0.0,
    step=1.0
)

new_yarn_delivered = st.checkbox("या आठवड्यात नवीन सूत आले आहे का?")
new_yarn_qty = 0.0

if new_yarn_delivered:
    new_yarn_qty = st.number_input(
        "नवीन आलेले सूत (kg)",
        min_value=0.0,
        step=1.0
    )

st.divider()

# ----------------- MACHINE INPUT -----------------
st.subheader("🏭 LOOM नुसार उत्पादन नोंद")

machine_meters = {}
remaining_stock = {}
all_meters = []

for machine in range(1, TOTAL_MACHINES + 1):
    with st.expander(f"LOOM {machine}", expanded=False):

        prev_stock = st.number_input(
            f"मागील शिल्लक टागे (LOOM {machine})",
            value=previous_machine_stock.get(machine, 0.0),
            min_value=0.0,
            step=0.25,
            key=f"prev_{machine}"
        )

        new_beam = st.checkbox(
            f"या LOOM {machine} वर नवीन बीम बसवली आहे का?",
            key=f"beam_{machine}"
        )

        if new_beam:
            beam_taga = st.number_input(
                f"नवीन बीमची टागे क्षमता (LOOM {machine})",
                min_value=0.0,
                step=0.25,
                key=f"beam_taga_{machine}"
            )
            prev_stock += beam_taga

        meter_input = st.text_area(
            f"या आठवड्यातील टाग्याचे मीटर (LOOM {machine})",
            placeholder="उदा: 80, 90, 75",
            key=f"meter_{machine}"
        )

        meters = []
        if meter_input.strip():
            try:
                meters = [float(x.strip()) for x in meter_input.split(",") if x.strip()]
            except:
                st.error("कृपया योग्य आकडे कॉमा ने वेगळे करून भरा")

        machine_meters[machine] = meters
        all_meters.extend(meters)

        produced = len(meters)
        remaining_stock[machine] = prev_stock - produced

        st.write(f"➡️ तयार झालेले टागे: **{produced}**")
        st.write(f"➡️ शिल्लक टागे: **{round(remaining_stock[machine], 2)}**")

st.divider()

# ----------------- CALCULATE & SAVE -----------------
if st.button("🔢 अंतिम निकाल काढा", type="primary"):

    total_taga = sum(len(machine_meters[m]) for m in machine_meters)
    total_meter = sum(all_meters)

    wastage = total_meter * WASTAGE_PERCENT / 100
    final_meter = total_meter - wastage
    yarn_required = final_meter * YARN_PER_METER

    total_yarn_available = previous_yarn_stock + new_yarn_qty
    remaining_yarn = total_yarn_available - yarn_required

    # -------- DISPLAY RESULT --------
    st.subheader("📊 आठवड्याचा अंतिम निकाल")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("एकूण टागे", total_taga)
        st.metric("एकूण मीटर", round(total_meter, 2))
        st.metric("अंतिम मीटर (1.5% वेस्टेज नंतर)", round(final_meter, 2))

    with col2:
        st.metric("लागणारे सूत (kg)", round(yarn_required, 3))
        st.metric("उपलब्ध सूत (kg)", round(total_yarn_available, 3))
        st.metric("शिल्लक सूत (kg)", round(remaining_yarn, 3))

    # -------- SAVE WEEKLY SUMMARY --------
    summary_row = pd.DataFrame([{
        "date": TODAY,
        "total_taga": total_taga,
        "total_meter": total_meter,
        "final_meter": final_meter,
        "yarn_required": yarn_required,
        "remaining_yarn": remaining_yarn
    }])

    if os.path.exists(SUMMARY_FILE):
        summary_row.to_csv(SUMMARY_FILE, mode="a", header=False, index=False)
    else:
        summary_row.to_csv(SUMMARY_FILE, index=False)

    # -------- SAVE MACHINE STOCK --------
    machine_rows = []
    for m in range(1, TOTAL_MACHINES + 1):
        machine_rows.append({
            "date": TODAY,
            "machine": m,
            "remaining_taga": remaining_stock[m]
        })

    df_machine_new = pd.DataFrame(machine_rows)

    if os.path.exists(MACHINE_FILE):
        df_machine_new.to_csv(MACHINE_FILE, mode="a", header=False, index=False)
    else:
        df_machine_new.to_csv(MACHINE_FILE, index=False)

    st.success("💾 आठवड्याचा डेटा कायमस्वरूपी सेव्ह झाला आहे")

# ----------------- SHOW ALL SAVED DATA -----------------
st.divider()
st.subheader("📋 सर्व आठवड्यांचा साठवलेला डेटा")

if os.path.exists(SUMMARY_FILE):
    df_summary = pd.read_csv(SUMMARY_FILE)
    st.dataframe(df_summary, use_container_width=True)

    st.download_button(
        "⬇️ Excel / CSV डाउनलोड करा",
        df_summary.to_csv(index=False),
        file_name="weekly_summary.csv",
        mime="text/csv"
    )
else:
    st.info("अजून कोणताही आठवड्याचा डेटा उपलब्ध नाही")
