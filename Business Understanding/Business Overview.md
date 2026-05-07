# RiskBeacon
## Business Overview

Project Overview
-------------------------------------------------------
**RiskBeacon** merupakan sebuah sistem analisis dan pemodelan credit scoring yang dirancang untuk membantu institusi keuangan, khususnya koperasi simpan pinjam, dalam menilai kelayakan kredit secara lebih objektif dan terukur. Sistem ini dibangun dengan merepresentasikan prinsip 5C of Credit : **Character, Capacity, Capital, Collateral, dan Condition** ke dalam pendekatan berbasis data historis. Dengan memanfaatkan variabel-variabel kuantitatif seperti pendapatan, rasio utang, serta riwayat keterlambatan pembayaran, **RiskBeacon** mampu menghasilkan estimasi risiko individu dalam bentuk probability of default dan credit score yang mudah dipahami oleh pengambil keputusan.

Permasalahan utama yang ingin diselesaikan oleh RiskBeacon terletak pada aspek **Character**, yang dalam praktik koperasi masih sering dinilai secara subjektif berdasarkan reputasi sosial atau kedekatan lingkungan. Pendekatan ini berpotensi menimbulkan bias dan ketidakkonsistenan dalam pengambilan keputusan kredit, sehingga meningkatkan risiko kesalahan dalam menilai anggota. RiskBeacon hadir untuk mengatasi keterbatasan tersebut dengan menggantikan penilaian subjektif menjadi evaluasi berbasis data, sehingga setiap keputusan didasarkan pada pola historis dan indikator risiko yang terukur.

Dari sisi bisnis, RiskBeacon ditargetkan mampu menyeimbangkan antara pengurangan risiko gagal bayar dan optimalisasi penyaluran kredit kepada debitur yang layak. Dengan adanya segmentasi risiko yang jelas (low, medium, high), koperasi dapat menerapkan strategi pemberian kredit yang lebih tepat, seperti penyesuaian limit atau kebijakan persetujuan. Dampak yang diharapkan adalah peningkatan kualitas portofolio pinjaman, penurunan tingkat kredit macet, serta terciptanya sistem pengambilan keputusan yang lebih konsisten, transparan, dan berkelanjutan.

Business Problem
-------------------------------------------------------
Koperasi simpan pinjam sering menghadapi **tingginya default rate** yang berdampak langsung pada kerugian finansial dan terganggunya arus kas. Hal ini diperparah oleh proses approval kredit tanpa risk control yang jelas, sehingga meningkatkan potensi **bad debt**. Selain itu, masih terdapat ketidakkonsistenan dalam pengambilan keputusan, di mana anggota dengan kondisi finansial serupa dapat memperoleh hasil berbeda akibat penilaian yang subjektif, terutama pada aspek karakter.

Di sisi lain, koperasi dihadapkan pada **trade-off antara risiko dan keuntungan**. Pendekatan yang terlalu restriktif memang lebih aman namun menurunkan potensi revenue, sedangkan pendekatan yang terlalu agresif dapat meningkatkan penyaluran kredit tetapi dengan risiko gagal bayar yang lebih tinggi. Fenomena ini tercermin dalam berbagai kasus nyata, seperti anggota yang kehilangan aset akibat gagal bayar pinjaman kecil, permasalahan kredit macet di koperasi daerah, hingga kasus ekstrem penagihan utang yang tidak manusiawi. Referensi kasus:

[Anggota Gagal Bayar 20jt, Rumah Disita Koperasi](https://regional.kompas.com/read/2025/09/09/153304878/kehilangan-rumah-usai-pinjam-rp-20-juta-di-koperasi-demak-hadi-punya-satu#)

[Kredit Macet 87% dari Total Aset](https://www.tempo.co/ekonomi/anggota-koperasi-melania-masih-berjuang-bongkar-dugaan-penggelapan-uang-rp-210-miliar-2064084)

[Menunggak Utang Rp19 Juta, Pegawai Koperasi Dikurung Selama 5 Hari | Liputan 6](https://www.youtube.com/watch?v=J2-U59WHvAY)

Business Objective
-------------------------------------------------------
Analisis dan Model yang kami bangun merepresentasikan prinsip 5C of Credit yang umum digunakan baik di perbankan maupun koperasi, dengan pendekatan berbasis data historis untuk meningkatkan objektivitas dalam penilaian kredit.

Secara spesifik projek ini menargetkan :
- Mengungkap risiko gagal bayar tersembunyi yang sebelumnya akan lolos tanpa pengawasan
- Meningkatkan perkiraan keuntungan per pinjaman
- Menunjukkan nominal pinjaman sesuai dengan data historis anggota

Business Impact Simulation (Conseptual)
-------------------------------------------------------
Scenario 1 : Tanpa Model
- Data anggota : 150.000 anggota
- Persentase resiko gagal bayar : 6.7%
Dari total anggota yang melakukan peminjaman, bisa dikatakan bahwa hampir semua peminjaman diterima oleh pihak koperasi

Scenario 2 : Dengan Model
- Total anggota : 100.000 anggota
- Persentase resiko gagal bayar : 28.5%
Dengan data historis anggota yang berbeda, terlihat peningkatan persentase resiko gagal bayar yang sangat signifikan. Ini bukan berarti tingkat gagal bayar meningkat, melainkan model berhasil mengungkap risiko gagal bayar yang tersembunyi.

Scenario 3 : Dengan scoring + limit
- Low Risk : High Limit (Limit = (1 - risk probability) x income)
- Medium Risk : Moderate Limit (Limit = 10% x income)
- High Risk : Reject
Dengan segmentasi tersebut, resiko lebih terkontrol dan revenue tetap berlangsung dengan baik.

Success Metrics
-------------------------------------------------------
Reject user dengan probability lebih dari 80%

Hasil dari setiap metrik yang kami dapati dari model projek :
- ROC-AUC : 0.92
- Recall : 0.74
- KS-Statistic : 0.58

dataset resouce : [Give Me Some Credit](https://www.kaggle.com/competitions/GiveMeSomeCredit/overview)
