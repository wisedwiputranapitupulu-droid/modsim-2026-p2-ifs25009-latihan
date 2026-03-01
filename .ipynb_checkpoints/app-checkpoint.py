import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ======================
# CONFIG HALAMAN
# ======================
st.set_page_config(
    page_title="Dashboard Analisis Kuesioner",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Dashboard Analisis Data Kuesioner")
st.markdown("Visualisasi interaktif skala Likert (SS–STS)")

# ======================
# LOAD FILE OTOMATIS
# ======================
try:
    df = pd.read_excel("data_kuesioner.xlsx")
except FileNotFoundError:
    st.error("File 'data_kuesioner.xlsx' tidak ditemukan di folder project.")
    st.stop()

# ======================
# KONVERSI SKALA
# ======================
skor_map = {
    "SS": 6,
    "S": 5,
    "CS": 4,
    "CTS": 3,
    "TS": 2,
    "STS": 1
}

df = df.replace(skor_map)
df = df.select_dtypes(include="number")

if df.empty:
    st.error("Tidak ada data yang valid.")
    st.stop()

# ======================
# SIDEBAR FILTER
# ======================
st.sidebar.header("⚙️ Filter Pertanyaan")

selected_questions = st.sidebar.multiselect(
    "Pilih Pertanyaan",
    df.columns,
    default=df.columns
)

df = df[selected_questions]

# ======================
# FORMAT LONG
# ======================
df_long = df.melt(var_name="Pertanyaan", value_name="Skor").dropna()

def kategori(skor):
    if skor >= 5:
        return "Positif"
    elif skor == 4:
        return "Netral"
    else:
        return "Negatif"

df_long["Kategori"] = df_long["Skor"].apply(kategori)

# ======================
# KPI METRICS
# ======================
col1, col2, col3, col4 = st.columns(4)

col1.metric("👥 Responden", df.shape[0])
col2.metric("❓ Pertanyaan", df.shape[1])
col3.metric("⭐ Rata-rata", round(df_long["Skor"].mean(), 2))
col4.metric("📊 Total Jawaban", df_long.shape[0])

st.divider()

# =====================================================
# 1️⃣ BAR CHART - DISTRIBUSI KESELURUHAN
# =====================================================
st.subheader("📈 Distribusi Jawaban Keseluruhan")

dist_all = df_long["Skor"].value_counts().sort_index()

fig1 = px.bar(
    x=dist_all.index,
    y=dist_all.values,
    text=dist_all.values,
    color=dist_all.index,
    color_continuous_scale="Viridis"
)

st.plotly_chart(fig1, use_container_width=True)

# =====================================================
# 2️⃣ DONUT CHART
# =====================================================
st.subheader("🥧 Proporsi Jawaban")

fig2 = px.pie(
    names=dist_all.index,
    values=dist_all.values,
    hole=0.5
)

st.plotly_chart(fig2, use_container_width=True)

# =====================================================
# 3️⃣ STACKED BAR
# =====================================================
st.subheader("📊 Distribusi per Pertanyaan")

stacked = df_long.groupby(["Pertanyaan", "Skor"]).size().reset_index(name="Jumlah")

fig3 = px.bar(
    stacked,
    x="Pertanyaan",
    y="Jumlah",
    color="Skor",
    barmode="stack"
)

st.plotly_chart(fig3, use_container_width=True)

# =====================================================
# 4️⃣ RATA-RATA PER PERTANYAAN
# =====================================================
st.subheader("🏆 Rata-rata Skor per Pertanyaan")

mean_score = df.mean().sort_values(ascending=False).reset_index()
mean_score.columns = ["Pertanyaan", "Rata-rata"]

fig4 = px.bar(
    mean_score,
    x="Rata-rata",
    y="Pertanyaan",
    orientation="h",
    text="Rata-rata",
    color="Rata-rata",
    color_continuous_scale="Plasma"
)

fig4.update_traces(texttemplate="%.2f")

st.plotly_chart(fig4, use_container_width=True)

best = mean_score.iloc[0]
worst = mean_score.iloc[-1]

st.success(f"🏆 Tertinggi: {best['Pertanyaan']} ({round(best['Rata-rata'],2)})")
st.error(f"📉 Terendah: {worst['Pertanyaan']} ({round(worst['Rata-rata'],2)})")

# =====================================================
# 5️⃣ DISTRIBUSI KATEGORI
# =====================================================
st.subheader("🎯 Distribusi Kategori Jawaban")

kategori_dist = df_long["Kategori"].value_counts().reset_index()
kategori_dist.columns = ["Kategori", "Jumlah"]

fig5 = px.bar(
    kategori_dist,
    x="Kategori",
    y="Jumlah",
    text="Jumlah",
    color="Kategori"
)

st.plotly_chart(fig5, use_container_width=True)

# =====================================================
# BONUS 1 - HEATMAP
# =====================================================
st.subheader("🔥 Heatmap Rata-rata")

heatmap_data = df.mean().to_frame(name="Rata-rata")

fig6 = go.Figure(
    data=go.Heatmap(
        z=[heatmap_data["Rata-rata"]],
        x=heatmap_data.index,
        y=["Skor"],
        colorscale="YlGnBu"
    )
)

st.plotly_chart(fig6, use_container_width=True)

# =====================================================
# BONUS 2 - BOXPLOT
# =====================================================
st.subheader("📦 Boxplot Distribusi Skor")

fig7 = px.box(
    df_long,
    x="Pertanyaan",
    y="Skor",
    color="Pertanyaan"
)

st.plotly_chart(fig7, use_container_width=True)
