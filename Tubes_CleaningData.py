import pandas as pd

data = pd.read_excel('data_wisata_bogor_FillHarga.xlsx')
df = pd.DataFrame(data)
df2 = df.drop_duplicates(subset=['nama_tempat_wisata'], keep='first')
df2['rating'] = pd.to_numeric(df2['rating'], errors='coerce').fillna(0)
df2['jumlah_rating'] = pd.to_numeric(df2['jumlah_rating'], errors='coerce').fillna(0)
df2['harga_tiket'] = pd.to_numeric(df2['harga_tiket'], errors='coerce').fillna(0)
df2.to_excel("data_wisata_bogor_Clean.xlsx", index=False)