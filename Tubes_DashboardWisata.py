import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import folium
from streamlit_folium import st_folium
import os

# =========================================================
# 1. KONFIGURASI HALAMAN
# =========================================================
st.set_page_config(page_title="Dashboard Strategis Wisata", layout="wide")

st.title("Dashboard Strategis Ketahanan Wisata")
st.markdown("Analisis performa destinasi berdasarkan kualitas (Rating) dan popularitas (Jumlah Ulasan).")
st.markdown("---")

# =========================================================
# 2. DATA PREPARATION & CLEANING
# =========================================================
@st.cache_data
def load_raw_data():
    file = 'data_wisata_bogor.xlsx'
    if os.path.exists(file):
        return pd.read_excel(file)
    return None

@st.cache_data
def load_data():
    file = 'data_wisata_bogor_Segmented.xlsx'
    if os.path.exists(file):
        df = pd.read_excel(file)
        return df
    return None

df_raw = load_raw_data()
df_clean = load_data()

if df_clean is not None:

    # =====================================================
    # AMBANG BATAS (MEDIAN)
    # =====================================================
    valid_data = df_clean[(df_clean['rating'] > 0) & (df_clean['jumlah_rating'] > 0)]
    med_rating = valid_data['rating'].median()
    med_jumlah = valid_data['jumlah_rating'].median()


    # =====================================================
    # SIDEBAR (INFO SAJA, TANPA FILTER)
    # =====================================================
    st.sidebar.header("Statistik Ambang Batas")
    st.sidebar.metric("Median Rating", f"{med_rating:.1f}")
    st.sidebar.metric("Median Ulasan", int(med_jumlah))

    st.sidebar.markdown("---")
    st.sidebar.subheader("Keterangan Warna")
    st.sidebar.success("Hijau: TANGGUH")
    st.sidebar.info("Biru: POTENSIAL")
    st.sidebar.warning("Oranye: RENTAN")
    st.sidebar.error("Merah: KURANG DIMINATI")

    # pakai semua data (tanpa filter segmen)
    df = df_clean.copy()

    # =====================================================
    # TAB
    # =====================================================
    tab_data, tab_stat, tab_map = st.tabs([
        "Data Detail",
        "Analisis Strategis",
        "Pemetaan & Harga Tiket",
    ])

    # =====================================================
    # TAB 1: DATA
    # =====================================================
    with tab_data:
        st.header("Dataset Wisata")
        st.subheader("Data Wisata Tersegmentasi")
        st.dataframe(
            df.reset_index(),
            column_config={
                "link_gambar": st.column_config.ImageColumn("Foto"),
                "harga_tiket": st.column_config.NumberColumn("Tiket (Rp)", format="Rp %d"),
                "rating": st.column_config.NumberColumn("Rating", format="%.1f"),
                "jumlah_rating": st.column_config.NumberColumn("Ulasan", format="%d"),
                "link": st.column_config.LinkColumn("Maps Link")
            },
            hide_index=True,
            use_container_width=True

        )
        st.subheader("Data Mentah")   
        st.dataframe(df_raw)
    # =====================================================
    # TAB 2: VISUALISASI
    # =====================================================
    with tab_stat:
        col_matriks, col_proporsi = st.columns([2, 1])

        with col_matriks:
            st.subheader("Matriks Kuadran (Rating vs Popularitas)")
            fig, ax = plt.subplots(figsize=(10, 6))

            colors_hex = {
                'TANGGUH': '#2ecc71',
                'POTENSIAL': '#3498db',
                'RENTAN': '#e67e22',
                'KURANG DIMINATI': '#e74c3c'
            }

            for label, color in colors_hex.items():
                subset = df[df['segmen_ketahanan'] == label]
                ax.scatter(
                    subset['jumlah_rating'],
                    subset['rating'],
                    c=color,
                    label=label,
                    alpha=0.6,
                    s=100,
                    edgecolors='w'
                )

            ax.set_xscale('log')
            ax.axhline(med_rating, color='black', linestyle='--', alpha=0.5)
            ax.axvline(med_jumlah, color='black', linestyle='--', alpha=0.5)
            ax.set_xlabel("Popularitas (Jumlah Ulasan - Skala Log)")
            ax.set_ylabel("Kualitas (Rating)")
            ax.legend()
            st.pyplot(fig)

        with col_proporsi:
            st.subheader("Proporsi Segmen")
            counts = df['segmen_ketahanan'].value_counts()

            fig_p, ax_p = plt.subplots(figsize=(6, 8))
            counts.plot(
                kind='bar',
                ax=ax_p,
                color=['#2ecc71', '#3498db', '#e67e22', '#e74c3c']
            )
            plt.xticks(rotation=45)
            plt.ylabel("Jumlah Destinasi")
            st.pyplot(fig_p)

        st.divider()
        st.subheader("Sebaran Segmen per Kategori Wisata")
        pivot_df = pd.crosstab(df['kategori'], df['segmen_ketahanan'])

        fig2, ax2 = plt.subplots(figsize=(12, 6))
        pivot_df.plot(
            kind='bar',
            stacked=True,
            color=['#e74c3c', '#3498db', '#e67e22', '#2ecc71'],
            ax=ax2
        )
        plt.xticks(rotation=30, ha='right')
        plt.legend(title="Segmen", bbox_to_anchor=(1.05, 1), loc='upper left')
        st.pyplot(fig2)

    # =====================================================
    # TAB 3: MAP (TOP 5 PER SEGMEN = 20 TITIK)
    # =====================================================
    with tab_map:
        st.header("Peta Lokasi Strategis (Top 5 per Segmen Ketahanan)")

        top_samples = []

        for seg in ['TANGGUH', 'POTENSIAL', 'RENTAN', 'KURANG DIMINATI']:
            seg_data = (
                df[df['segmen_ketahanan'] == seg]
                .sort_values(by=['rating', 'jumlah_rating'], ascending=False)
                .head(5)
            )

            if not seg_data.empty:
                top_samples.append(seg_data)

        df_map = pd.concat(top_samples)

        m = folium.Map(
            location=[df_map['latitude'].mean(), df_map['longitude'].mean()],
            zoom_start=11
        )

        colors_folium = {
            'TANGGUH': 'green',
            'POTENSIAL': 'blue',
            'RENTAN': 'orange',
            'KURANG DIMINATI': 'red'
        }

        for _, row in df_map.iterrows():
            warna_pin = colors_folium.get(row['segmen_ketahanan'], 'gray')

            harga_display = (
                f"Rp {int(row['harga_tiket']):,}".replace(",", ".")
                if row['harga_tiket'] > 0
                else "Gratis / Tdk Diketahui"
            )

            popup_html = f"""
            <div style="width: 200px; font-family: sans-serif;">
                <b>{row['nama_tempat_wisata']}</b><br>
                <small>{row['kategori']}</small>
                <hr>
                <b>Rating:</b> {row['rating']}<br>
                <b>Ulasan:</b> {int(row['jumlah_rating'])}<br>
                <b>Tiket:</b> {harga_display}
                <div style="margin-top: 8px; background:{warna_pin}; color:white;
                            text-align:center; border-radius:4px;">
                    {row['segmen_ketahanan']}
                </div>
            </div>
            """

            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=row['nama_tempat_wisata'],
                icon=folium.Icon(color=warna_pin, icon='info-sign')
            ).add_to(m)

        st_folium(m, width="100%", height=600)
        st.info(f"Menampilkan {len(df_map)} destinasi unggulan (20 titik).")


else:
    st.error("File tidak ditemukan.")