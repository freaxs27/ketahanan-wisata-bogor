import pandas as pd

data = pd.read_excel('data_wisata_bogor_HasilScrap.xlsx')

df = pd.DataFrame(data)


valid_data = df[df['rating'].notna() & (df['jumlah_rating'] > 0)]

# 3. Hitung Median untuk masing-masing kolom 
median_rating = valid_data['rating'].median()
median_jumlah_ulasan = valid_data['jumlah_rating'].median()


# 4. Tambahan: Melihat Median per Kategori 
median_per_kategori = valid_data.groupby('kategori')['rating'].median()
print(f"\nMedian Rating per Kategori:")
print(median_per_kategori)

def klasifikasi_ketahanan(row):
    r = row['rating']
    j = row['jumlah_rating']

    if r >= median_rating and j >= median_jumlah_ulasan:
        return 'TANGGUH'
    elif r >= median_rating and j < median_jumlah_ulasan:
        return 'POTENSIAL'
    elif r < median_rating and j >= median_jumlah_ulasan:
        return 'RENTAN'
    else:
        return 'KURANG DIMINATI'

# Eksekusi: Membuat kolom baru berdasarkan fungsi di atas
df['segmen_ketahanan'] = df.apply(klasifikasi_ketahanan, axis=1)

df.to_excel("data_wisata_bogor_Segmented.xlsx", index=False)
