Project: Analisis Risiko Kredit

1. Summary: Default Overview
Analisis ini mengidentifikasi pola kritis yang membedakan nasabah "Lancar" dan "Gagal Bayar". Berdasarkan dataset 150.000 entri, ditemukan bahwa perilaku historis dan beban finansial merupakan prediktor yang signifikan secara statistik.

Temuan Kunci: Kelompok nasabah dengan data anomali pada frekuensi keterlambatan (kategori "Unknown") memiliki Default Rate tinggi (~60%). Hal ini membuktikan bahwa anomali input seringkali menjadi indikator adanya risiko tersembunyi yang tidak terlaporkan.

2. Risk Patterns & Business Insights

A. Behavioral Risk (The "Red Flags")

Extreme Delay: Nasabah dengan riwayat keterlambatan pembayaran menunjukkan korelasi yang sangat kuat dengan risiko gagal bayar. Frekuensi keterlambatan lebih dari 6 kali hampir memastikan terjadinya default di masa depan (risiko mencapai >60%).

Utilization Stress: Nasabah yang menggunakan limit kredit hingga kapasitas penuh (Very High Utilization) memiliki risiko default 3x lebih tinggi dari rata-rata. Ini menunjukkan ketergantungan pada utang untuk arus kas sehari-hari (over-leveraged).

B. Customer Profile & Capacity

Age Profile: Terdapat korelasi terbalik antara usia dan risiko; kelompok usia muda (<30 tahun) menunjukkan profil risiko paling tinggi (~12%).

Financial Burden: Terdapat tren meningkat pada variabel tanggungan (dependents). Risiko default cenderung naik seiring bertambahnya beban finansial rumah tangga, dengan titik risiko tertinggi pada nasabah dengan 6 tanggungan.

Income Capacity: Nasabah dengan kategori pendapatan "Low" memiliki kerentanan lebih tinggi dibandingkan nasabah berpendapatan tinggi, yang memperkuat pengaruh kapasitas ekonomi terhadap kepatuhan pembayaran.
