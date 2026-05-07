# RiskBeacon — Pipeline Penilaian Risiko Kredit Otomatis dengan Analitik Prediktif dan Monitoring Real-Time

> **Meminimalkan kerugian akibat gagal bayar, sambil tetap memberikan kredit kepada anggota yang layak.**

---

## Daftar Isi

- [Tentang Proyek](#tentang-proyek)
- [Latar Belakang Bisnis](#latar-belakang-bisnis)
- [Tujuan dan Objektif](#tujuan-dan-objektif)
- [Dataset](#dataset)
- [Arsitektur Sistem](#arsitektur-sistem)
- [Gambaran Pipeline](#gambaran-pipeline)
- [Analisis Data Eksploratif](#analisis-data-eksploratif)
- [Pemodelan](#pemodelan)
- [Simulasi Dampak Bisnis](#simulasi-dampak-bisnis)
- [Logika Keputusan Kredit](#logika-keputusan-kredit)
- [Struktur Proyek](#struktur-proyek)
- [Teknologi yang Digunakan](#teknologi-yang-digunakan)
- [Tim](#tim)
- [Referensi](#referensi)

---

## Tentang Proyek

**RiskBeacon** adalah sistem penilaian risiko kredit yang dirancang untuk menilai dan memantau probabilitas gagal bayar anggota sebelum keputusan kredit diambil.

RiskBeacon mentransformasi data historis peminjam menjadi **keputusan kredit yang objektif dan berbasis data** melalui pipeline analisis dan pemodelan terintegrasi yang berlandaskan prinsip **5C of Credit** — Character, Capacity, Capital, Collateral, dan Conditions.

Sistem ini dibangun untuk melayani **lembaga perbankan** maupun **koperasi simpan pinjam**, menjembatani kesenjangan antara penilaian kredit berbasis kepercayaan sosial dengan analitik prediktif modern.

### Komponen Sistem

| Komponen | Deskripsi |
|---|---|
| **Data Pipeline & Quality Monitoring** | Ingesti, transformasi, dan validasi data historis peminjam — menangani missing value, outlier, dan ketidakseimbangan kelas |
| **Exploratory Data Analysis** | Insight bisnis dari perilaku peminjam yang dipetakan ke framework 5C |
| **Predictive Modeling** | Model klasifikasi LightGBM untuk mengestimasi Probabilitas Gagal Bayar (PD) di level individu |
| **Model Explainability** | Atribusi fitur berbasis SHAP untuk menjelaskan skor risiko setiap peminjam |
| **Operational Risk Monitoring** | Segmentasi risiko ke dalam tiga tier — Low, Medium, dan High — berdasarkan distribusi PD Score |

---

## Latar Belakang Bisnis

Seiring institusi keuangan — dari bank hingga koperasi simpan pinjam — terus memperluas jangkauannya, penilaian kredit yang subjektif tetap menjadi risiko operasional yang kritis. Ketergantungan berlebih pada reputasi sosial dan pertimbangan informal dapat menyebabkan:

- Meningkatnya Non-Performing Loan (NPL)
- Keputusan kredit yang tidak konsisten dan rentan bias
- Kerugian finansial akibat gagal bayar yang sebenarnya dapat dicegah

Khususnya dalam konteks **Koperasi Simpan Pinjam**, dimensi `Character` pada penilaian 5C kredit masih sangat bergantung pada reputasi sosial — bukan berasal dari data atau angka. Hal ini menciptakan blind spot yang dirancang khusus untuk diatasi oleh RiskBeacon.

> *"Sebelum RiskBeacon diterapkan, tingkat gagal bayar aktual sebesar 6,7% dari 150.000 data peminjam tidak terdeteksi pada level individu. Setelah model prediktif diterapkan pada 100.000 data peminjam yang berbeda, RiskBeacon mengidentifikasi 28,5% pemohon sebagai berindikasi gagal bayar — mengungkap risiko tersembunyi yang sebelumnya akan lolos tanpa pengawasan."*

---

## Tujuan dan Objektif

1. Membangun pipeline otomatis end-to-end dari data Excel mentah hingga penilaian risiko kredit
2. Merepresentasikan framework **5C of Credit** melalui fitur data dan desain model
3. Menghasilkan **skor Probabilitas Gagal Bayar (PD Score)** untuk setiap anggota
4. Mensegmentasi anggota ke dalam tier **Low / Medium / High Risk**
5. Memberikan rekomendasi limit kredit berdasarkan tier risiko
6. Meminimalkan NPL sambil tetap mempertahankan akses kredit bagi anggota yang layak

---

## Dataset

| Properti | Detail |
|---|---|
| Sumber | [Give Me Some Credit — Kaggle](https://www.kaggle.com/datasets/brycecf/give-me-some-credit-dataset) |
| Asal | Kompetisi Credit Fusion, Kaggle 2011 |
| Jumlah baris training | 150.000 |
| Jumlah fitur | 11 kolom |
| Variabel target | `SeriousDlqin2yrs` (1 = gagal bayar, 0 = tidak gagal bayar) |
| Ketidakseimbangan kelas | ~6,7% tingkat gagal bayar |

### Pemetaan Fitur ke 5C of Credit

| Fitur | Dimensi 5C | Makna Bisnis |
|---|---|---|
| `SeriousDlqin2yrs` | — | Target: gagal bayar dalam 2 tahun |
| `RevolvingUtilizationOfUnsecuredLines` | Capacity | % limit kartu kredit yang sudah terpakai |
| `Age` | Character | Usia anggota — proksi panjang riwayat kredit |
| `NumberOfTime30-59DaysPastDueNotWorse` | Character | Sinyal awal: keterlambatan 30–59 hari |
| `DebtRatio` | Capacity | Total cicilan bulanan / penghasilan bulanan |
| `MonthlyIncome` | Capacity | Indikator utama kemampuan membayar |
| `NumberOfOpenCreditLinesAndLoans` | Capital | Total kewajiban kredit aktif |
| `NumberOfTimes90DaysLate` | Character | Sinyal terkuat: riwayat tunggak 90+ hari |
| `NumberRealEstateLoansOrLines` | Collateral | Kredit berbasis properti — menurunkan risiko |
| `NumberOfTime60-89DaysPastDueNotWorse` | Character | Sinyal keterlambatan menengah |
| `NumberOfDependents` | Capital | Beban finansial dari tanggungan keluarga |

---

## Arsitektur Sistem

```
Data Excel (Koperasi)
        │
        ▼
   Upload ke Storage
        │
        ▼
┌─────────────────────────────┐
│   Apache Airflow DAG        │
│  ┌─────────────────────┐    │
│  │ Extract             │    │
│  │ Validasi Skema      │    │
│  │ Transform           │    │
│  │ Load ke Database    │    │
│  └─────────────────────┘    │
└─────────────────────────────┘
        │
        ▼
   Exploratory Data Analysis
   (Seleksi Fitur WoE + IV)
        │
        ▼
┌─────────────────────────────┐
│   Model LightGBM            │
│  Train / Test Split 80:20   │
│  Hyperparameter Tuning      │
│  Evaluasi: AUC, Recall,     │
│  KS-Statistic, SHAP         │
└─────────────────────────────┘
        │
        ▼
   PD Score per Anggota (0,0 – 1,0)
        │
   ┌────┴────────┬────────────┐
   ▼             ▼            ▼
Low Risk     Medium Risk   High Risk
Limit Tinggi Limit Sedang  Ditolak
```

---

## Gambaran Pipeline

### ETL — Apache Airflow

| Tahap | Proses |
|---|---|
| **Extract** | Baca file Excel → parse ke DataFrame |
| **Validate** | Cek skema, tipe data, duplikasi — kirim notifikasi error ke admin jika tidak valid |
| **Transform** | Imputasi missing value, penanganan outlier, encoding, feature engineering |
| **Load** | Simpan data bersih ke database / data lake |

### Analisis & Pemodelan

| Tahap | Proses |
|---|---|
| **EDA** | Analisis distribusi, heatmap korelasi, pengecekan ketidakseimbangan kelas |
| **Seleksi Fitur** | Weight of Evidence (WoE) + Information Value (IV) |
| **Pemodelan** | LightGBM dengan penanganan imbalance (SMOTE / class weight) |
| **Evaluasi** | ROC-AUC, Recall, KS-Statistic, explainability SHAP |

---

## Analisis Data Eksploratif

Temuan utama dari EDA:

- **Ketidakseimbangan kelas**: 93,3% tidak gagal bayar vs 6,7% gagal bayar — memerlukan SMOTE atau pembobotan kelas
- **Prediktor terkuat** (berdasarkan IV): `NumberOfTimes90DaysLate`, `RevolvingUtilizationOfUnsecuredLines`, `NumberOfTime30-59DaysPastDueNotWorse`
- **DebtRatio** memiliki outlier signifikan yang memerlukan pemotongan berbasis IQR
- **MonthlyIncome** memiliki ~20% missing value — diimputasi menggunakan median per kelompok usia


---

## Pemodelan

### Model: LightGBM

LightGBM dipilih karena performa unggulnya pada data tabular yang tidak seimbang, kemampuan penanganan missing value bawaan, dan kecepatan training yang cocok untuk deployment pipeline produksi.

### Metrik Evaluasi

| Metrik | Fungsi dalam Konteks Kredit |
|---|---|
| **ROC-AUC** | Kekuatan diskriminasi keseluruhan model |
| **Recall** | Metrik prioritas — meminimalkan default yang tidak terdeteksi (False Negative = kerugian finansial nyata) |
| **KS-Statistic** | Standar industri perbankan — pemisahan maksimum antara distribusi gagal bayar dan tidak gagal bayar |
| **SHAP** | Explainability — membenarkan keputusan kredit individual kepada petugas dan regulator |

> **Mengapa Recall lebih diprioritaskan daripada Precision?**
> Dalam risiko kredit, False Negative (memprediksi aman padahal akan gagal bayar) secara langsung menggerus modal institusi. False Positive (menolak peminjam yang sebenarnya aman) adalah peluang yang terlewat — menyakitkan namun tidak mengancam kelangsungan institusi. Oleh karena itu Recall menjadi target optimasi utama.

### Interpretasi KS-Statistic

| Nilai KS | Kualitas Model |
|---|---|
| < 0,20 | Sangat lemah — bangun ulang |
| 0,20 – 0,40 | Cukup memadai |
| 0,40 – 0,60 | Bagus — siap produksi |
| 0,60 – 0,75 | Sangat bagus |
| > 0,75 | Sangat tinggi — validasi potensi overfitting |

### Hasil Metrik yang Didapatkan
- Nilai KS-Statistic : 0.58

- Nilai ROC-AUC : 0.92

- Nilai Recall : 0.74

---

## Simulasi Dampak Bisnis

| | Sebelum (Baseline) | Sesudah (Model Diterapkan) |
|---|---|---|
| Populasi | 150.000 data peminjam | 100.000 data peminjam |
| Tingkat gagal bayar | 6,7% (aktual) | 28,5% (prediksi) |
| Interpretasi | Distribusi nyata di data training | Model mengungkap risiko tersembunyi di populasi baru |

> *Sebelum: distribusi gagal bayar aktual dari data training (n=150.000). Sesudah: hasil prediksi model pada populasi peminjam baru yang belum pernah dilihat sebelumnya (n=100.000). Tingginya prediksi gagal bayar mencerminkan kemampuan model dalam mengidentifikasi pola risiko yang tidak terlihat melalui penilaian manual.*

**Estimasi dampak finansial**: Dari populasi 80.000 peminjam, RiskBeacon mengidentifikasi ~22.800 pemohon berisiko tinggi. Dengan asumsi rata-rata pinjaman Rp 5.000.000, penolakan proaktif berpotensi mencegah estimasi kerugian hingga **Rp 114 miliar** dari kredit bermasalah.

---

## Logika Keputusan Kredit

Threshold PD Score ditentukan dari titik cut-off optimal KS-Statistic dan distribusi persentil PD Score pada data training.

| Segmen Risiko | PD Score | Keputusan Kredit | Limit |
|---|---|---|---|
| 🟢 **Low Risk** | < 0,43 | Disetujui | Limit tinggi — suku bunga standar |
| 🟡 **Medium Risk** | 0,43 – 0,53 | Disetujui dengan review | Limit moderat — review manual oleh petugas |
| 🔴 **High Risk** | ≥ 0,53 | Ditolak | Tidak ada kredit — rujukan edukasi keuangan |

> Catatan: Threshold dikalibrasi berdasarkan tingkat gagal bayar portofolio (~6,7%) dan titik pemisahan optimal KS-Statistic. Threshold ini bukan konstanta tetap — rekalibrasi disarankan ketika diterapkan pada populasi peminjam baru.

---

## Struktur Proyek

```
├── dags/                              # File DAG Apache Airflow
│   └── etl_pipeline.py
├── notebooks/
│   ├── 01_eda.ipynb                   # Analisis Data Eksploratif
│   ├── 02_feature_engineering.ipynb   # WoE, IV, feature engineering
│   ├── 03_modeling.ipynb              # Training & evaluasi LightGBM
│   └── 04_shap_explainability.ipynb   # Explainability SHAP
├── src/
│   ├── preprocessing.py
│   ├── feature_selection.py           # WoE + IV
│   └── model.py
├── data/
│   ├── raw/                           # cs-training.csv
│   └── processed/
├── outputs/
│   ├── model/                         # Model LightGBM tersimpan
│   └── reports/                       # Metrik evaluasi, plot SHAP
├── requirements.txt
└── README.md
```

---

## Teknologi yang Digunakan

| Layer | Teknologi |
|---|---|
| **Orkestrasi** | Apache Airflow |
| **Pemrosesan Data** | Python, Pandas, NumPy |
| **Feature Engineering** | Scikit-learn, Weight of Evidence (custom) |
| **Pemodelan** | LightGBM |
| **Explainability** | SHAP |
| **Penanganan Imbalance** | Imbalanced-learn (SMOTE) |
| **Evaluasi** | Metrik Scikit-learn, KS-Statistic |
| **Penyimpanan** | PostgreSQL / CSV |
| **Visualisasi** | Matplotlib, Seaborn |
| **Version Control** | Git, GitHub |

---

## Tim

**FTDS Batch 037 — Hacktiv8 | Group 001**

| Nama | Peran |
|---|---|
| Austin Silitonga | Lead Project — Business Understanding |
| Hernanda Rifaldi | Data Engineer — ETL Pipeline & Airflow |
| Kesyia Patty | Data Analyst — EDA & Business Insight |
| M.Nabil | Data Scientist — Feature Engineering & Modeling |
| Rezha Aulia | Data Scientist — SHAP & KS-Statistic |

---

## Referensi

- Dataset Give Me Some Credit — [Kaggle](https://www.kaggle.com/datasets/brycecf/give-me-some-credit-dataset)
- Credit Fusion & Will Cukierski. *Give Me Some Credit*. Kompetisi Kaggle, 2011
- Pendekatan IRB Basel II/III — Bank for International Settlements
- OJK POJK No.40/POJK.03/2019 — Kualitas Aset Bank Umum
- Siddiqi, N. (2006). *Credit Risk Scorecards*. Wiley
- SHAP: Lundberg & Lee (2017). *A Unified Approach to Interpreting Model Predictions*

---

<p align="center">
  Dibangun dengan tujuan — menjadikan kredit lebih adil, objektif, dan berbasis data.<br>
  <strong>RiskBeacon</strong> · FTDS Batch 037 · Hacktiv8 · 2025
</p>
