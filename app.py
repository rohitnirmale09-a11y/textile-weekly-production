import streamlit as st

# ----------------- CONSTANTS -----------------
TOTAL_MACHINES = 7
WASTAGE_PERCENT = 1.5
YARN_PER_METER = 0.2854

# ----------------- APP TITLE -----------------
st.set_page_config(page_title="Textile Production System", layout="wide")

st.title("🧵 Textile Weekly Production System")
st.write("Professional calculation for meter, wastage & yarn stock")

st.divider()

# ----------------- YARN STOCK INPUT -----------------
st.subheader("🧶 Yarn Stock Input")

previous_yarn_stock = st.number_input(
    "Previous Yarn Stock (kg)", min_value=0.0, step=1.0
)

new_yarn_delivered = st.checkbox("New yarn delivered this week?")
new_yarn_qty = 0.0

if new_yarn_delivered:
    new_yarn_qty = st.number_input(
        "New Yarn Delivered (kg)", min_value=0.0, step=1.0
    )

st.divider()

# ----------------- MACHINE INPUT -----------------
st.subheader("🏭 Machine-wise Production Entry")

machine_meters = {}
remaining_stock = {}
all_meters = []

for machine in range(1, TOTAL_MACHINES + 1):
    with st.expander(f"Machine {machine}", expanded=False):

        prev_stock = st.number_input(
            f"Previous Remaining Taga Stock (Machine {machine})",
            min_value=0.0,
            step=0.25,
            key=f"prev_{machine}"
        )

        new_beam = st.checkbox(
            f"New beam added on Machine {machine}?",
            key=f"beam_{machine}"
        )

        if new_beam:
            beam_taga = st.number_input(
                f"Taga capacity of new beam (Machine {machine})",
                min_value=0.0,
                step=0.25,
                key=f"beam_taga_{machine}"
            )
            prev_stock += beam_taga

        meter_input = st.text_area(
            f"Enter taga meters for Machine {machine} (comma separated)",
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

        st.write(f"➡️ Current Produced Taga: **{produced}**")
        st.write(f"➡️ Remaining Taga Stock: **{round(remaining_stock[machine], 2)}**")

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
        st.metric("Total Taga Produced", total_taga)
        st.metric("Total Meter Produced", round(total_meter, 2))
        st.metric("Final Meter (after 1.5% wastage)", round(final_meter, 2))

    with col2:
        st.metric("Yarn Required (kg)", round(yarn_required, 3))
        st.metric("Total Yarn Available (kg)", round(total_yarn_available, 3))
        st.metric("Remaining Yarn (kg)", round(remaining_yarn, 3))

    st.success("✅ Calculation completed successfully")
