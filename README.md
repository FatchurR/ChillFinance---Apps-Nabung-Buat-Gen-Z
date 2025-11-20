# 💸 ChillFinance – Aplikasi Nabung buat Gen Z

**by FatchurR**

## 🧠 Deskripsi Singkat

**ChillFinance** adalah aplikasi sederhana berbasis **CLI (Command Line Interface)** yang dirancang untuk membantu **generasi Z** agar lebih bijak dalam mengelola keuangannya.
Melalui aplikasi ini, pengguna bisa **menabung, mencatat pengeluaran, melihat saldo, dan menganalisis kondisi keuangan pribadi** secara mudah.

Aplikasi ini menggunakan **library bawaan Python**, sehingga ringan dan dapat dijalankan di semua sistem operasi tanpa instalasi tambahan.

---

## 🎯 Tujuan Program

Mendorong kebiasaan menabung dan membantu pengguna mengatur keuangan secara mandiri dengan cara yang sederhana namun efektif.

Fitur ini cocok untuk Gen Z yang sering kesulitan menyisihkan uang, agar bisa belajar mengatur pemasukan dan pengeluaran harian.

---

## 🚀 Cara Menjalankan Aplikasi

### Windows

```bash
python chillfinance.py
```

Atau jika Python belum ditambahkan ke PATH:

```bash
python3 chillfinance.py
```

### Linux

```bash
python3 chillfinance.py
```

Jika Anda ingin menjalankan dengan chmod:

```bash
chmod +x chillfinance.py
./chillfinance.py
```

### macOS

```bash
python3 chillfinance.py
```

Atau gunakan Homebrew jika Python belum terinstall:

```bash
brew install python3
python3 chillfinance.py
```

> **Catatan:** Pastikan Python 3.6+ sudah terinstall di sistem Anda. Cek dengan menjalankan `python --version` atau `python3 --version`.

---

## ⚙️ Cara Kerja (Workflow)

1. **Halaman Login Awal**

   * Pilihan:
     `1. Login`
     `2. Register`
     `3. Keluar`
2. **Menu Register**

   * Input nama pengguna (3–32 karakter)
   * Input password (min. 6 karakter, konfirmasi password)
3. **Menu Login**

   * Input username dan password (case-insensitive)
4. **Menu Utama**

   ```
   1. Set Target Tabungan
   2. Nabung (Uang Masuk)
   3. Catat Pengeluaran (Uang Keluar)
   4. Lihat Saldo & Progress
   5. Lihat Riwayat Transaksi
   6. Analisis Keuangan
   7. Logout
   ```
5. **Logout**

   * Sistem akan menanyakan:
     “Apakah Anda ingin backup data? (Y/n)”
     Jika *Ya*, data akan disimpan otomatis dalam format `.csv`.

---

## 📦 Struktur Data

Data pengguna disimpan sementara dalam **dictionary (RAM)**, berisi:

```python
{
  "nama": "Fatchur",
  "saldo": 1000000,
  "target": 2000000,
  "history": [
      ["2025-11-10", "nabung", 500000, "uang jajan disisihkan"],
      ["2025-11-11", "keluar", 200000, "beli kaos"]
  ]
}
```

---

## 🧉 Penjelasan Setiap Menu

### 1. Set Target Tabungan

* Input jumlah target (contoh: `1.000.000`)
* Input tujuan menabung (contoh: `Beli PC`)
* Data disimpan di atribut `user.target`

---

### 2. Nabung (Uang Masuk)

* Input jumlah uang masuk
* Input catatan (opsional)
* `saldo += jumlah`
* Riwayat dicatat: `[tanggal, "nabung", jumlah, catatan]`

---

### 3. Catat Pengeluaran (Uang Keluar)

* Input jumlah pengeluaran
* Jika `saldo >= jumlah` → saldo dikurangi
* Jika `saldo < jumlah` → saldo disisakan 30% dari jumlah dan dibatasi tarik 1x per tahun
* Riwayat dicatat: `[tanggal, "keluar", jumlah, catatan]`

---

### 4. Lihat Saldo & Progress

Menampilkan:

* Saldo saat ini
* Target tabungan
* Persentase progress
* Progress bar contoh:

  ```
  [#####-----] (50%)
  ```

---

### 5. Lihat Riwayat Transaksi

Format tampilan:

```
Tanggal | Jenis | Jumlah | Catatan
```

---

### 6. Analisis Keuangan

Menghitung:

* Total Nabung
* Total Pengeluaran
* Saldo Akhir (Netto)

Menampilkan status keuangan:

| Kriteria               | Kondisi                 | Status               |
| ---------------------- | ----------------------- | -------------------- |
| ≥ 70% target tercapai  | Pengeluaran wajar       | 💰 Dompet sehat 😎   |
| 40–69% target tercapai | Pengeluaran agak tinggi | ⚖️ Cukup seimbang    |
| < 40% target tercapai  | Pengeluaran berlebihan  | 😭 Boros tipis-tipis |

---

## 🧱 Aturan Validasi Input

1. **Username/Nama:**
   3–32 karakter, huruf/angka/`_`/`-`/spasi, *case-insensitive* saat login.
2. **Password:**
   Minimal 6 karakter, konfirmasi password wajib.
   *(Gunakan `getpass` agar tidak terlihat saat diketik)*
3. **Nominal Uang:**
   Hanya angka, boleh menggunakan `.` atau `,` sebagai pemisah ribuan (dibersihkan otomatis).
4. **Catatan:**
   Opsional, maksimal 120 karakter.
5. **Konfirmasi Aksi:**
   Untuk tindakan penting (logout, backup) gunakan prompt `Y/n` dengan default `Y`.
6. **Error Handling:**
   Jika input tidak valid, tampilkan alasan dan minta input ulang.

---

## 💾 Backup & Restore Data

* Saat logout, sistem menawarkan backup dalam file `.csv`.
* Data yang di-backup berisi: `nama`, `saldo`, `target`, dan seluruh `riwayat transaksi`.
* Dapat dipulihkan kembali jika fitur restore ditambahkan di versi selanjutnya.

---

## 🧮 Teknologi yang Digunakan

* **Python Standard Library Only**

  * `getpass` → untuk input password tersembunyi
  * `csv` → untuk backup data
  * `datetime` → untuk mencatat tanggal transaksi
  * `os` → untuk validasi file dan tampilan CLI

---

## 📚 Dokumentasi & Guide Book

Untuk panduan lengkap dan dokumentasi lebih detail, kunjungi:

* [🎓 User Guide](https://docs.google.com/document/d/1NQyktSJHHV8sd8_ybvAOpqO3vroNz86VSxmkAx_WX6g/edit?usp=sharing) 

---

## 📌 Catatan Pengembang

> Aplikasi ini dibuat sebagai proyek pembelajaran pemrograman Python tingkat dasar-menengah.
> Tujuan utamanya adalah melatih **logika berpikir sistematis, pengelolaan data, serta validasi input pengguna.**
