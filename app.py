import streamlit as st

# ----------------- CONSTANTS -----------------
TOTAL_MACHINES = 7
WASTAGE_PERCENT = 1.5
YARN_PER_METER = 0.02854

# ----------------- APP TITLE -----------------
st.set_page_config(page_title="Textile Production System", layout="wide")

st.title("🧵 SUDHIR TEXTILE")
st.write("Professional calculation for meter, wastage & yarn stock")

st.divider()

# ----------------- YARN STOCK INPUT -----------------
st.subheader("🧶 सुताचे स्टॉक")

previous_yarn_stock = st.number_input(
    "मागील सुताचे स्टॉक (kg)", min_value=0.0, step=1.0
)

new_yarn_delivered = st.checkbox("नविन आलेले बाचके")
new_yarn_qty = 0.0

if new_yarn_delivered:
    new_yarn_qty = st.number_input(
        "ऐकून बाचके किलोमध्ये (kg)", min_value=0.0, step=1.0
    )

st.divider()

# ----------------- MACHINE INPUT -----------------
st.subheader("🏭 LOOM-wise Production Entry")

machine_meters = {}
remaining_stock = {}
all_meters = []

for machine in range(1, TOTAL_MACHINES + 1):
    with st.expander(f"LOOM {machine}", expanded=False):

        prev_stock = st.number_input(
            f"मागील शिल्लक कतस्स (Machine {machine})",
            min_value=0.0,
            step=0.25,
            key=f"prev_{machine}"
        )

        new_beam = st.checkbox(
            f"नवीन बिंब {machine}?",
            key=f"beam_{machine}"
        )

        if new_beam:
            beam_taga = st.number_input(
                f"कतस्स (Machine {machine})",
                min_value=0.0,
                step=0.25,
                key=f"beam_taga_{machine}"
            )
            prev_stock += beam_taga

        meter_input = st.text_area(
            f"मीटर {machine} (comma separated)",
            placeholder="Example: 80, 90, 75",
            key=f"meter_{machine}"
        )

        meters = []
        if meter_input.strip():
            try:
                meters = [float(x.strip()) for x in meter_input.split(",") if x.strip()]
            except:
                st.error("Please enter valid numbers separated by commas")

        machine_meters[machine] = meters
        all_meters.extend(meters)

        produced = len(meters)
        remaining_stock[machine] = prev_stock - produced

        st.write(f"➡️ ऐकून तागे: **{produced}**")
        st.write(f"➡️ शिल्लक कतस्स: **{round(remaining_stock[machine], 2)}**")

st.divider()

# ----------------- CALCULATE BUTTON -----------------
if st.button("🔢 Calculate Final Result", type="primary"):

    total_taga = sum(len(machine_meters[m]) for m in machine_meters)
    total_meter = sum(all_meters)

    wastage = total_meter * WASTAGE_PERCENT / 100
    final_meter = total_meter - wastage
    yarn_required = final_meter * YARN_PER_METER

    total_yarn_available = previous_yarn_stock + new_yarn_qty
    remaining_yarn = total_yarn_available - yarn_required

    st.subheader("📊 Final Weekly Summary")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("ऐकून तागे", total_taga)
        st.metric("ऐकून मीटर", round(total_meter, 2))
        st.metric("मीटर (after 1.5% wastage)", round(final_meter, 2))

    with col2:
        st.metric("लागणारे सूत (kg)", round(yarn_required, 3))
        st.metric("ऐकून सूत (kg)", round(total_yarn_available, 3))
        st.metric("शिल्लक सूत (kg)", round(remaining_yarn, 3))

    st.success("✅ Calculation completed successfully")
