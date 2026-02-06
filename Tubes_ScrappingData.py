import requests
from bs4 import BeautifulSoup
import pandas as pd

# 1. AMBIL HTML DARI NETLIFY
url = "https://data-wisata-bogor-clean.netlify.app//"
headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

# 2. AMBIL SEMUA ROW DATA
rows = soup.find_all("tr", class_="wisata-row")

print(f"DEBUG: row ditemukan = {len(rows)}")

data = []

for row in rows:
    def get_text(class_name):
        cell = row.find("td", class_=f"wisata-cell {class_name}")
        return cell.get_text(strip=True) if cell else None

    data.append({
        "nama_tempat_wisata": get_text("wisata-nama_tempat_wisata"),
        "kategori": get_text("wisata-kategori"),
        "preferensi": get_text("wisata-preferensi"),
        "kecamatan": get_text("wisata-kecamatan"),
        "kabupaten_kota": get_text("wisata-kabupaten_kota"),
        "rating": get_text("wisata-rating"),
        "jumlah_rating": get_text("wisata-jumlah_rating"),
        "harga_tiket": get_text("wisata-harga_tiket"),
        "link": get_text("wisata-link"),
        "latitude": get_text("wisata-latitude"),
        "longitude": get_text("wisata-longitude"),
        "link_gambar": get_text("wisata-link_gambar"),
    })

# 3. KE DATAFRAME
df = pd.DataFrame(data)

# 4. EXPORT KE EXCEL
df.to_excel("data_wisata_bogor_HasilScrap.xlsx", index=False)

print("✅ SCRAPING BERHASIL")
print(f"📊 Total data: {len(df)} baris")
print("📁 Output: ata_wisata_bogor_HasilScrap.xlsx")
