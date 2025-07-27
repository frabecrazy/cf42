import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Digital Carbon Footprint Calculator", layout="wide")

# Init session state
if "page" not in st.session_state or st.session_state.page not in ["intro", "main", "results"]:
    st.session_state.page = "intro"
if "role" not in st.session_state:
    st.session_state.role = ""
if "device_inputs" not in st.session_state:
    st.session_state.device_inputs = {}
if "results" not in st.session_state:
    st.session_state.results = {}
activity_factors = {
    "Student": {
        "MS Office (e.g. Excel, Word, PPT…)": 0.00901,
        "Technical softwares (e.g. Matlab, Python…)": 0.00901,
        "Web browsing": 0.0264,
        "Watching lecture recordings": 0.0439,
        "Online classes streaming or video call": 0.112,
        "Reading study materials on your computer (e.g. slides, articles, digital textbooks)": 0.00901
    },
    "Professor": {
        "MS Office (e.g. Excel, Word, PPT…)": 0.00901,
        "Web browsing": 0.0264,
        "Videocall (e.g. Zoom, Teams…)": 0.112,
        "Online classes streaming": 0.112,
        "Reading materials on your computer (e.g. slides, articles, digital textbooks)": 0.00901,
        "Technical softwares (e.g. Matlab, Python…)": 0.00901
    },
    "Staff Member": {
        "MS Office (e.g. Excel, Word, PPT…)": 0.00901,
        "Management software (e.g. SAP)": 0.00901,
        "Web browsing": 0.0264,
        "Videocall (e.g. Zoom, Teams…)": 0.112,
        "Reading materials on your computer (e.g. documents)": 0.00901
    }
}

ai_factors = {
    "Summarize texts or articles": 0.000711936,
    "Translate sentences or texts": 0.000363008,
    "Explain a concept": 0.000310784,
    "Generate quizzes or questions": 0.000539136,
    "Write formal emails or messages": 0.000107776,
    "Correct grammar or style": 0.000107776,
    "Analyze long PDF documents": 0.001412608,
    "Write or test code": 0.002337024,
    "Generate images": 0.00206,
    "Brainstorm for thesis or projects": 0.000310784,
    "Explain code step-by-step": 0.003542528,
    "Prepare lessons or presentations": 0.000539136
}

device_ef = {
    "Desktop Computer": 296,
    "Laptop Computer": 170,
    "Smartphone": 38.4,
    "Tablet": 87.1,
    "External Monitor": 235,
    "Headphones": 12.17,
    "Printer": 62.3,
    "Router/Modem": 106
}

eol_modifier = {
    "I bring it to a certified e-waste collection center": -0.0384,
    "I throw it away in general waste": 0.0595,
    "I return it to manufacturer for recycling or reuse": -0.3461,
    "I sell or donate it to someone else": -0.6991,
    "I store it at home, unused": 0.0113
}


def show_main():
    st.title("☁️ Digital Usage Form")

    # === DEVICES ===
    st.header("💻 Devices")
    st.markdown("""
Choose the digital devices you currently use, and for each one, provide a few details about how you use it and what you do when it's no longer needed.

- **Years of use**: Estimate how many years you've used (or plan to use) the device in total.
- **Condition**:
    - *New*: You were the first owner of the device when it was purchased.
    - *Used*: The device was previously owned or refurbished when you started using it.
- **Ownership**:
    - *Personal*: You’re the only one who regularly uses the device.
    - *Shared*: The device is used by other people in your household or team.
- **End-of-life behavior**: What do you usually do with your devices when you stop using them? (e.g. recycle, donate, store in a drawer...)
""")

    if "device_list" not in st.session_state:
        st.session_state.device_list = []

    device_to_add = st.selectbox("Select a device and click 'Add Device', repeat for all the devices you own", list(device_ef.keys()))
    if st.button("➕ Add Device"):
        count = sum(d.startswith(device_to_add) for d in st.session_state.device_list)
        new_id = f"{device_to_add}_{count}"
        st.session_state.device_list.append(new_id)
        st.session_state.device_inputs[new_id] = {
            "years": 1.0,
            "used": "New",
            "shared": "Personal",
            "eol": "I bring it to a certified e-waste collection center"
        }

    total_prod, total_eol = 0, 0

    for device_id in st.session_state.device_list:
        base_device = device_id.rsplit("_", 1)[0]
        st.subheader(base_device)

        prev = st.session_state.device_inputs[device_id]
        col1, col2, col3, col4 = st.columns(4)

        years = col1.number_input("Years of use", 0.5, 20.0, step=0.5, format="%.1f", key=f"{device_id}_years")
        used = col2.selectbox("Condition", ["New", "Used"], index=["New", "Used"].index(prev["used"]), key=f"{device_id}_used")
        shared = col3.selectbox("Ownership", ["Personal", "Shared"], index=["Personal", "Shared"].index(prev["shared"]), key=f"{device_id}_shared")
        eol = col4.selectbox("End-of-life behavior", list(eol_modifier.keys()), index=list(eol_modifier.keys()).index(prev["eol"]), key=f"{device_id}_eol")

        st.session_state.device_inputs[device_id] = {
            "years": years,
            "used": used,
            "shared": shared,
            "eol": eol
        }

        if st.button(f"🗑 Remove {base_device}", key=f"remove_{device_id}"):
            st.session_state.device_list.remove(device_id)
            st.session_state.device_inputs.pop(device_id, None)
            st.rerun()

        impact = device_ef[base_device]
        if used == "New" and shared == "Personal":
            adj_years = years
        elif used == "Used" and shared == "Personal":
            adj_years = years + (years / 2)
        elif used == "New" and shared == "Shared":
            adj_years = years * 3
        else:
            adj_years = years * 4.5

        eol_mod = eol_modifier[eol]
        prod_per_year = impact / adj_years
        eol_impact = (impact * eol_mod) / adj_years

        total_prod += prod_per_year
        total_eol += eol_impact

        st.markdown(f"📊 **Production**: {prod_per_year:.2f} kg CO₂e/year &nbsp;&nbsp;&nbsp; **End-of-life**: {eol_impact:.2f} kg CO₂e/year")

    # === DIGITAL ACTIVITIES ===
    st.header("🎓 Digital Activities")
    st.markdown("""
Estimate how many hours per day you spend on each activity during a typical 8-hour study or work day.  
You may exceed 8 hours if multitasking (e.g., watching a lecture while writing notes).
""")

    role = st.session_state.role
    ore_dict = {}
    digital_total = 0

    for act, ef in activity_factors[role].items():
        ore = st.number_input(f"{act} (h/day)", 0.0, 8.0, 0.0, 0.5, key=act)
        ore_dict[act] = ore
        digital_total += ore * ef * 250

    st.markdown("Now tell us more about your habits related to email, cloud, printing and connectivity.")

    email_plain = st.selectbox("Emails sent/received during a typical 8-hour day **no attachments** - do not include spam emails", ["1–3", "4–10", "11–25", "26–50", "> 50"])
    email_attach = st.selectbox("Emails sent/received during a typical 8-hour day **with attachments** - do not include spam emails", ["1–3", "4–10", "11–25", "26–50", "> 50"])
    emails = {"1–3": 2, "4–10": 7, "11–25": 18, "26–50": 38, "> 50": 55}

    cloud = st.selectbox("Cloud storage you currently use **for academic or work-related files** (e.g., on iCloud, Google Drive, OneDrive)", ["<5GB", "5–20GB", "20–50GB", "50–100GB"])
    cloud_gb = {"<5GB": 3, "5–20GB": 13, "20–50GB": 35, "50–100GB": 75}

    wifi = st.slider("Estimate your daily Wi-Fi connection time during a typical 8-hour study or work day, including hours when you're not actively using your device (e.g., background apps, idle mode)", 0.0, 8.0, 4.0, 0.5)
    pages = st.number_input("Number of pages you print per day for academic or work purposes", 0, 100, 0)

    idle = st.radio("When you're not using your computer...", ["I turn it off", "I leave it on (idle mode)", "I don’t have a computer"])

    mail_total = emails[email_plain] * 0.004 * 250 + emails[email_attach] * 0.035 * 250 + cloud_gb[cloud] * 0.01
    wifi_total = wifi * 0.00584 * 250
    print_total = pages * 0.0045 * 250
    idle_total = 250 * 0.0001536 * 16 if idle == "I leave it on (idle mode)" else 0

    digital_total += mail_total + wifi_total + print_total + idle_total

    # === AI TOOLS ===
    st.header("🤖 AI Tools")
    st.markdown("Estimate how many queries you make per day for each AI-powered task.")

    ai_total = 0
    cols = st.columns(2)
    for i, (task, ef) in enumerate(ai_factors.items()):
        with cols[i % 2]:
            q = st.number_input(f"{task} (queries/day)", 0, 100, 0, key=task)
            ai_total += q * ef * 250

    # === FINAL BUTTON ===
    if st.button("🌍 Discover Your Digital Carbon Footprint!"):
        st.session_state.results = {
            "Devices": total_prod,
            "E-Waste": total_eol,
            "Digital Activities": digital_total,
            "AI Tools": ai_total
        }
        st.session_state.page = "results"
        st.rerun()


def show_intro():
    st.title("📱 Digital Carbon Footprint Calculator")

    st.markdown("""
Welcome to the **Digital Carbon Footprint Calculator**, a tool developed within the *Green DiLT* project to raise awareness about the hidden environmental impact of digital habits in academia.

This calculator is tailored for **university students, professors, and staff members**, helping you estimate your CO₂e emissions from everyday digital activities — often overlooked, but increasingly relevant.

---

👉 Select your role to begin:
""")

    st.session_state.role = st.selectbox(
        "What is your role in academia?",
        ["", "Student", "Professor", "Staff Member"]
    )

    if st.button("➡️ Start Calculation"):
        if st.session_state.role:
            st.session_state.page = "main"
            st.rerun()
        else:
            st.warning("Please select your role before continuing.")

def show_results():
    st.title("🌍 Your Digital Carbon Footprint")

    res = st.session_state.results
    total = sum(res.values())

    st.metric("🌱 Total CO₂e", f"{total:.0f} kg/year")
    st.divider()

    st.metric("💻 Devices", f"{res['Devices']:.2f} kg")
    st.metric("🗑️ E-Waste", f"{res['E-Waste']:.2f} kg")
    st.metric("📡 Digital Activities", f"{res['Digital Activities']:.2f} kg")
    st.metric("🤖 AI Tools", f"{res['AI Tools']:.2f} kg")

    st.divider()
    st.subheader("📊 Breakdown by Category")
    df_plot = pd.DataFrame({
        "Category": ["Devices", "Digital Activities", "Artificial Intelligence", "E-Waste"],
        "CO₂e (kg)": [res["Devices"], res["Digital Activities"], res["AI Tools"], res["E-Waste"]]
    })
    st.bar_chart(df_plot.set_index("Category"))

    most_impact_cat = df_plot.sort_values("CO₂e (kg)", ascending=False).iloc[0]["Category"]

    detailed_tips = {
        "Devices": [
"**Turn off devices when not in use** - Even in standby mode, they consume energy. Powering them off saves electricity and extends their lifespan.",  

"**Update software regularly** - This enhances efficiency and performance, often reducing energy consumption.",  

"**Activate power-saving settings, reduce screen brightness and enable dark mode** – This lowers energy use.",  

"**Choose accessories made from recycled or sustainable materials** - This minimizes the environmental impact of your tech choices." 
        ],
        "Digital Activities": [
"**Use your internet mindfully** - Close unused apps, avoid sending large attachments, and turn off video during calls when not essential.",  

"**Declutter your digital space** - Regularly delete unnecessary files, empty trash and spam folders, and clean up cloud storage to reduce digital pollution.",  

"**Share links instead of attachments** - For example, link to a document on OneDrive or Google Drive instead of attaching it in an email.",  

"**Use instant messaging for short, urgent messages** - It's more efficient than email for quick communications."  
        ],
        "Artificial Intelligence": [
"**Use search engines for simple tasks** - They consume far less energy than AI tools.",  

"**Disable AI-generated results in search engines** - (e.g., on Bing: go to Settings > Search > Uncheck 'Include AI-powered answers' or similar option)",  

"**Prefer smaller AI models when possible** - For basic tasks, use lighter versions like GPT-4o-mini instead of more energy-intensive models.",  

"**Be concise in AI prompts and require concise answers** - short inputs and outputs require less processing"  
        ],
        "E-Waste": [
"**Avoid upgrading devices every year** - Extending device lifespan significantly reduces environmental impact.",  

"**Repair instead of replacing** - Fix broken electronics whenever possible to avoid unnecessary waste.",  

"**Consider buying refurbished devices** - They’re often as good as new, but with a much lower environmental footprint.",  

"**Recycle unused electronics properly** - Don’t store old devices at home: e-waste contains polluting and valuable materials that need specialized treatment."  
        ]
    }

    st.subheader(f"💡 Your biggest impact comes from: **{most_impact_cat}**")
    for tip in detailed_tips[most_impact_cat]:
        st.markdown(f"- {tip}")

    # Extra tips from other categories
    other_categories = [cat for cat in detailed_tips if cat != most_impact_cat]
    extra_tips = [random.choice(detailed_tips[cat]) for cat in random.sample(other_categories, 3)]

    st.subheader("🌍 Some Extra Tips:")
    for tip in extra_tips:
        st.markdown(f"- {tip}")

    st.divider()
    st.subheader("♻️ With the same emissions, you could…")
    burger_eq = total / 4.6
    led_days_eq = (total / 0.256) / 24
    car_km_eq = total / 0.17
    st.markdown(f"""
- 🍔 **Produce ~{burger_eq:.0f} beef burgers**
- 💡 **Keep 100 LED bulbs on for ~{led_days_eq:.0f} days**
- 🚗 **Drive a gasoline car for ~{car_km_eq:.0f} km**
""")

    st.markdown("### 🌱 You did it! Just by completing this tool, you're already part of the solution.")
    st.write("Digital emissions are invisible but not insignificant. Awareness is the first step toward change!")

    if st.button("↺ Restart"):
        st.session_state.clear()
        st.session_state.page = "intro"
        st.rerun()

# === PAGE NAVIGATION ===
if st.session_state.page == "intro":
    show_intro()
elif st.session_state.page == "main":
    show_main()
elif st.session_state.page == "results":
    show_results()


