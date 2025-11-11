import csv
import os
import sys
import time
from datetime import datetime
from getpass import getpass

# ========================
#  UTILITAS & VALIDASI
# ========================

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def slow_print(text):
    for c in text:
        print(c, end='', flush=True)
        time.sleep(0.005)
    print()

def valid_username(username):
    import re
    if not (3 <= len(username) <= 32):
        return False, "Username harus 3–32 karakter."
    if not re.fullmatch(r"[A-Za-z0-9_\-\s]+", username):
        return False, "Username hanya boleh berisi huruf, angka, spasi, _ atau -."
    return True, ""

def valid_password(pw):
    if len(pw) < 6:
        return False, "Password minimal 6 karakter."
    return True, ""

def input_nominal(prompt):
    while True:
        val = input(prompt).replace(".", "").replace(",", "")
        if not val.isdigit():
            print("❌ Hanya boleh angka, gunakan titik/koma untuk pemisah ribuan.")
            continue
        nominal = int(val)
        if nominal <= 0:
            print("❌ Nominal harus lebih dari 0.")
            continue
        return nominal

def input_catatan():
    note = input("Catatan (opsional, max 120 karakter): ").strip()
    if len(note) > 120:
        print("❌ Catatan terlalu panjang (maks 120 karakter).")
        return input_catatan()
    return note if note else "-"

def konfirmasi_aksi(prompt="Yakin lanjut? (Y/n): ", default="Y"):
    val = input(prompt).strip().lower()
    if val == "":
        return default.lower() == "y"
    return val in ["y", "yes"]

# ========================
#  STRUKTUR DATA
# ========================

users = {}

# Struktur data user
# {
#   "username": {
#       "password": "...",
#       "saldo": 0,
#       "target": 0,
#       "tujuan": "",
#       "riwayat": []
#   }
# }

# ========================
#  AUTENTIKASI
# ========================

def register():
    clear()
    print("=== REGISTER AKUN ===")
    while True:
        username = input("Masukkan Username: ").strip()
        valid, msg = valid_username(username)
        if not valid:
            print("❌", msg)
            continue
        uname_lower = username.lower()
        if uname_lower in users:
            print("❌ Username sudah terdaftar.")
            continue
        break

    while True:
        pw = getpass("Masukkan Password: ")
        valid, msg = valid_password(pw)
        if not valid:
            print("❌", msg)
            continue
        confirm_pw = getpass("Konfirmasi Password: ")
        if pw != confirm_pw:
            print("❌ Password tidak cocok.")
            continue
        break

    users[uname_lower] = {
        "username": username,
        "password": pw,
        "saldo": 0,
        "target": 0,
        "tujuan": "",
        "riwayat": []
    }
    print("✅ Registrasi berhasil!")
    input("Tekan Enter untuk login...")
    return login()

def login():
    clear()
    print("=== LOGIN ===")
    uname = input("Username: ").strip().lower()
    pw = getpass("Password: ")

    if uname not in users or users[uname]["password"] != pw:
        print("❌ Username atau password salah.")
        input("Tekan Enter untuk ulangi...")
        return login()

    print(f"✅ Selamat datang, {users[uname]['username']}!")
    return uname

# ========================
#  FITUR MENU UTAMA
# ========================

def set_target(user):
    print("\n=== SET TARGET TABUNGAN ===")
    target = input_nominal("Masukkan target tabungan: Rp ")
    tujuan = input("Masukkan tujuan menabung: ")
    users[user]["target"] = target
    users[user]["tujuan"] = tujuan
    print("✅ Target tabungan disimpan.")

def nabung(user):
    print("\n=== NABUNG (UANG MASUK) ===")
    jumlah = input_nominal("Masukkan jumlah uang: Rp ")
    catatan = input_catatan()
    users[user]["saldo"] += jumlah
    users[user]["riwayat"].append(
        [datetime.now().strftime("%Y-%m-%d %H:%M"), "nabung", jumlah, catatan]
    )
    print("✅ Transaksi nabung berhasil.")

def pengeluaran(user):
    print("\n=== CATAT PENGELUARAN ===")
    jumlah = input_nominal("Masukkan jumlah pengeluaran: Rp ")
    catatan = input_catatan()
    saldo = users[user]["saldo"]

    if saldo >= jumlah:
        users[user]["saldo"] -= jumlah
    else:
        print("⚠️ Saldo tidak cukup.")
        users[user]["saldo"] = int(saldo * 0.3)
        print("Saldo disesuaikan menjadi 30% dari saldo sebelumnya.")

    users[user]["riwayat"].append(
        [datetime.now().strftime("%Y-%m-%d %H:%M"), "keluar", jumlah, catatan]
    )
    print("✅ Pengeluaran dicatat.")

def lihat_saldo(user):
    print("\n=== SALDO & PROGRESS ===")
    saldo = users[user]["saldo"]
    target = users[user]["target"]
    tujuan = users[user]["tujuan"]

    print(f"Tujuan: {tujuan}")
    print(f"Saldo Saat Ini: Rp {saldo:,}")
    print(f"Target Tabungan: Rp {target:,}")
    if target > 0:
        progress = int((saldo / target) * 100)
        bar_length = 20
        filled = int(bar_length * progress / 100)
        bar = "#" * filled + "-" * (bar_length - filled)
        print(f"Progress: [{bar}] {progress}%")
    else:
        print("Belum ada target tabungan.")

def lihat_riwayat(user):
    print("\n=== RIWAYAT TRANSAKSI ===")
    riwayat = users[user]["riwayat"]
    if not riwayat:
        print("Belum ada transaksi.")
        return

    # Header tabel
    print("-" * 65)
    print(f"{'Tanggal':<20} | {'Tipe':<10} | {'Jumlah (Rp)':>12} | {'Catatan':<15}")
    print("-" * 65)
    for tgl, tipe, jumlah, catatan in riwayat:
        print(f"{tgl:<20} | {tipe:<10} | {jumlah:>12,} | {catatan:<15}")
    print("-" * 65)

def analisis_keuangan(user):
    print("\n=== ANALISIS KEUANGAN ===")
    total_nabung = sum(j[2] for j in users[user]["riwayat"] if j[1] == "nabung")
    total_keluar = sum(j[2] for j in users[user]["riwayat"] if j[1] == "keluar")

    if total_nabung == 0:
        print("Belum ada data tabungan.")
        return

    rasio = (total_keluar / total_nabung) * 100
    if rasio < 30:
        status = "Dompet Sehat 😎"
    elif 30 <= rasio <= 60:
        status = "Keuangan Cukup Stabil 🙂"
    else:
        status = "Boros Banget 😭"

    print(f"Total Nabung: Rp {total_nabung:,}")
    print(f"Total Pengeluaran: Rp {total_keluar:,}")
    print(f"Rasio Pengeluaran: {rasio:.2f}%")
    print(f"Status: {status}")

def backup_data(user):
    filename = f"{users[user]['username']}_backup.csv"
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Tanggal", "Tipe", "Jumlah", "Catatan"])
        writer.writerows(users[user]["riwayat"])
    print(f"✅ Data berhasil dibackup ke {filename}")

# ========================
#  MENU UTAMA
# ========================

def menu(user):
    while True:
        print("\n========== ChillFinance | by FatchurR ==========")
        print(f"User: {users[user]['username']} | Saldo: Rp {users[user]['saldo']:,}")
        print("1. Set Target Tabungan")
        print("2. Nabung (Uang Masuk)")
        print("3. Catat Pengeluaran")
        print("4. Lihat Saldo & Progress")
        print("5. Lihat Riwayat Transaksi")
        print("6. Analisis Keuangan")
        print("7. Logout")

        pilihan = input("Pilih menu: ").strip()
        if pilihan == "1":
            set_target(user)
        elif pilihan == "2":
            nabung(user)
        elif pilihan == "3":
            pengeluaran(user)
        elif pilihan == "4":
            lihat_saldo(user)
        elif pilihan == "5":
            lihat_riwayat(user)
        elif pilihan == "6":
            analisis_keuangan(user)
        elif pilihan == "7":
            if konfirmasi_aksi("Yakin logout dan backup data? (Y/n): "):
                backup_data(user)
            print("👋 Logout berhasil. Sampai jumpa!")
            break
        else:
            print("❌ Pilihan tidak valid.")

# ========================
#  PROGRAM UTAMA
# ========================

def main():
    clear()
    slow_print("===== ChillFinance - Apps Nabung buat Gen Z =====")
    while True:
        print("\n1. Login")
        print("2. Register")
        print("3. Keluar")
        pilih = input("Pilih menu: ").strip()
        if pilih == "1":
            user = login()
            menu(user)
        elif pilih == "2":
            user = register()
            menu(user)
        elif pilih == "3":
            print("Terima kasih telah menggunakan ChillFinance 💸")
            sys.exit()
        else:
            print("❌ Pilihan tidak valid.")

if __name__ == "__main__":
    main()
