import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import calendar

# --- CONFIGURATION DU SITE ---
st.set_page_config(page_title="Bejin Rainfall Report", page_icon="🌧️")

st.title("🌧️ TATITRA NY ROTSAK'ORANA: BEJIN (2018-2024)")
st.markdown("**Tatitra natao ho an'ny Mpanjifa sy ny Tantsaha**")
st.write("---")

# --- 1. FAMPIDIRANA DATA ---
# Eto dia afaka manafatra ilay fichier csv mivantana isika
# Na mampiasa ilay fichier efa eo (local)
try:
    # Raha eo amin'ny PC-nao ihany no anaovana azy:
    file_path = 'beijing_2018_2024_weather.csv'
    df = pd.read_csv(file_path)
    
    # Fanadiovana
    df.columns = df.columns.str.strip().str.lower()
    if 'precipitation_mm' in df.columns:
        df.rename(columns={'precipitation_mm': 'rainfall'}, inplace=True)
    elif 'precip' in df.columns:
         df.rename(columns={'precip': 'rainfall'}, inplace=True)

    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month

except Exception as e:
    st.error(f"Tsy hita ny rakitra CSV na misy olana: {e}")
    st.stop()

# --- 2. KAJY (CALCULATIONS) ---
yearly_rain = df.groupby('year')['rainfall'].sum()
avg_rain = yearly_rain.mean()
anomaly = yearly_rain - avg_rain

monthly_avg = df.groupby('month')['rainfall'].sum() / 7
wettest_month_idx = monthly_avg.idxmax()
wettest_month_name = calendar.month_name[wettest_month_idx]

# --- 3. FAMPISEHOANA (DISPLAY) ---

# Fizarana 1: Key Metrics (Chiffres Clés)
st.subheader("1. SALAN'ISA ANKAPOBENY")
col1, col2, col3 = st.columns(3)
col1.metric("Salan'isa Isan-taona", f"{avg_rain:.1f} mm")
col2.metric("Volana be orana", wettest_month_name)
col3.metric("Max Orana (Moyenne)", f"{monthly_avg.max():.1f} mm")

# Fizarana 2: Tabilao (Dataframe)
st.subheader("2. FIRONANA ISAN-TAONA (Data Table)")

# Fanamboarana table kely madio
summary_data = []
for year, rain in yearly_rain.items():
    anom_val = anomaly[year]
    status = "Normal"
    if anom_val > (avg_rain * 0.15): status = "Wet (Manorana be)"
    elif anom_val < -(avg_rain * 0.15): status = "Dry (Maina)"
    
    summary_data.append({
        "Taona": year,
        "Orana (mm)": f"{rain:.2f}",
        "Status": status
    })

st.table(pd.DataFrame(summary_data))

# Fizarana 3: Insights
st.subheader("3. TOROHEVITRA HO AN'NY TANTSAHA")
wet_months = monthly_avg[monthly_avg > 100].count()

if wet_months >= 5:
    st.success("✅ **Sata Tsara:** Mety tsara amin'ny fambolena VARY satria lava ny fotoam-pahavaratra.")
elif wet_months >= 3:
    st.warning("⚠️ **Sata Antonony:** Aleo mamboly KATSAKA na TSARAMASO (Tsingerina fohy).")
else:
    st.error("🛑 **Sata Maina:** Tandremo ny hain-tany! Mila voly mahatanty hafanana (Mangahazo, Sorgho).")

# Fizarana 4: Sary (Charts)
st.subheader("4. SARY FAMAKAFAKANA (Visualizations)")

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))
plt.subplots_adjust(hspace=0.4)

# Chart 1
colors = ['#1f77b4' if x >= 0 else '#d62728' for x in anomaly]
ax1.bar(yearly_rain.index, anomaly, color=colors, alpha=0.8)
ax1.axhline(0, color='black', linewidth=1)
ax1.set_title('Fironana (Anomaly) vs Salan\'isa', fontsize=12)
ax1.set_ylabel('Elanelana (mm)')

# Chart 2
ax2.plot(monthly_avg.index, monthly_avg, marker='o', color='green')
ax2.fill_between(monthly_avg.index, monthly_avg, color='green', alpha=0.1)
ax2.set_xticks(range(1, 13))
ax2.set_xticklabels([calendar.month_abbr[i] for i in range(1, 13)])
ax2.set_title('Saisonnalité (Isam-bolana)', fontsize=12)

st.pyplot(fig)

# Bokotra hamoahana Excel (Download)
st.write("---")
st.download_button(
    label="📥 Télécharger ny Tatitra (Excel)",
    data="Mila code fanampiny raha tiana ho tena Excel, fa ity dia ohatra fotsiny.",
    file_name="bejin_report.txt"
)