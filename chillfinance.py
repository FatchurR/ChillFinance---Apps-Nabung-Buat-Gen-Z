import csv
import os
import sys
import termios
import tty
import time
from datetime import datetime, timedelta
from getpass import getpass

# ========================
#  UTILITAS & VALIDASI
# ========================

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

# ANSI color helpers
def color(text, code):
    return f"\033[{code}m{text}\033[0m"

def bold(text):
    return f"\033[1m{text}\033[0m"

def cyan(text):
    return color(text, '36')

def green(text):
    return color(text, '32')

def yellow(text):
    return color(text, '33')

def red(text):
    return color(text, '31')

def magenta(text):
    return color(text, '35')

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

import sys
import termios
import tty

def format_rupiah_input(angka_str):
    """Format angka menjadi tampilan Rp style Indonesia (10.000,00)"""
    if not angka_str:
        return ""
    angka_int = int(angka_str)
    return f"{angka_int:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")

def input_nominal(prompt):
    """Input nominal realtime dengan format otomatis 10.000,00"""
    print(prompt, end="", flush=True)
    angka_str = ""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        while True:
            ch = sys.stdin.read(1)
            if ch == "\r" or ch == "\n":  # Enter
                print()
                if not angka_str:
                    print("❌ Input kosong. Masukkan nominal.")
                    return input_nominal(prompt)
                nominal = int(angka_str)
                if nominal <= 0:
                    print("❌ Nominal harus lebih dari 0.")
                    return input_nominal(prompt)
                return nominal
            elif ch == "\x7f":  # Backspace
                if len(angka_str) > 0:
                    angka_str = angka_str[:-1]
                    sys.stdout.write("\r" + " " * 50 + "\r")  # Hapus baris
                    sys.stdout.write(prompt + format_rupiah_input(angka_str))
                    sys.stdout.flush()
            elif ch.isdigit():
                calon = angka_str + ch
                # Batasi maksimal 1 triliun (1.000.000.000.000)
                if int(calon) > 1_000_000_000_000:
                    sys.stdout.write("\r" + " " * 70 + "\r")
                    sys.stdout.write(prompt + format_rupiah_input(angka_str))
                    sys.stdout.flush()
                    continue  # Abaikan input tambahan
                angka_str = calon
                sys.stdout.write("\r" + " " * 70 + "\r")
                sys.stdout.write(prompt + format_rupiah_input(angka_str))
                sys.stdout.flush()
            else:
                # Abaikan karakter non-digit
                pass
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def input_catatan():
    while True:
        note = input("Catatan (opsional, max 120 karakter): ").strip()
        if len(note) > 120:
            print("❌ Catatan terlalu panjang (maks 120 karakter).")
            continue
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

# ========================
#  AUTENTIKASI
# ========================

def register():
    clear()
    print(bold(cyan("📝 REGISTER AKUN")))
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
        "saldo_utama": 0,
        "targets": {},
        "riwayat": [],
        "last_withdraw": None,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    print("✅ Registrasi berhasil!")
    input("Tekan Enter untuk login...")
    return login()

def login():
    clear()
    print(bold(cyan("🔑 LOGIN")))
    uname = input("Username: ").strip().lower()
    pw = getpass("Password: ")

    if uname not in users or users[uname]["password"] != pw:
        print("❌ Username atau password salah.")
        input("Tekan Enter untuk ulangi...")
        return login()

    print(f"✅ Selamat datang, {users[uname]['username']}!")
    return uname

# ========================
#  FITUR TARGET
# ========================

def set_target(user):
    while True:
        print("\n" + bold(magenta("🎯 KELOLA TARGET TABUNGAN")))
        print(f"{green('➕')} 1. Tambah Target Baru")
        print(f"{cyan('📋')} 2. Lihat Daftar Target")
        print(f"{red('🗑️')} 3. Hapus Target")
        print(f"{yellow('↩️')} 4. Kembali")
        pilih = input(bold("Pilih: ")).strip()
        if pilih == "1":
            nama = input("Nama Target (unik): ").strip()
            if not nama:
                print("❌ Nama target tidak boleh kosong.")
                continue
            key = nama.lower()
            if any(k.lower() == key for k in users[user]["targets"].keys()):
                print("❌ Target dengan nama tersebut sudah ada.")
                continue
            target_amt = input_nominal("Masukkan nominal target: Rp ")
            users[user]["targets"][nama] = {
                "target": target_amt,
                "saldo": 0,
                "status": "aktif",
                "riwayat": [],
                "last_withdraw": None  # <== Tambahan
            }
            print(green(f"✅ Target '{nama}' dibuat (Rp {target_amt:,})."))

        elif pilih == "2":
            print("\n" + bold(cyan("--- Daftar Target ---")))
            targets = users[user]["targets"]
            if not targets:
                print("(Belum ada target)")
            else:
                for idx, (tname, tdata) in enumerate(targets.items(), 1):
                    t_target = tdata["target"]
                    t_saldo = tdata["saldo"]
                    pct = int((t_saldo / t_target) * 100) if t_target > 0 else 0
                    if pct >= 100:
                        pct = 100
                        status = "✅ Selesai"
                    else:
                        status = "Aktif"
                    bar_len = 20
                    filled = int(bar_len * pct / 100)
                    bar = "#" * filled + "-" * (bar_len - filled)
                    print(f"{idx}. {tname} → Rp {t_saldo:,} / Rp {t_target:,} ({pct}%) {status}")
                    print(f"   Progress: [{green(bar)}]")
            input("Tekan Enter untuk kembali...")
        elif pilih == "3":
            targets = users[user]["targets"]
            if not targets:
                print("Tidak ada target untuk dihapus.")
                continue
            print(bold(red("Pilih target untuk dihapus:")))
            names = list(targets.keys())
            for i, n in enumerate(names, 1):
                print(f"{i}. {n}")
            sel = input("Masukkan nomor (atau kosong untuk batal): ").strip()
            if not sel:
                continue
            if not sel.isdigit() or not (1 <= int(sel) <= len(names)):
                print("❌ Pilihan tidak valid.")
                continue
            idx = int(sel) - 1
            nama_hapus = names[idx]
            if konfirmasi_aksi(f"Yakin hapus target '{nama_hapus}'? (Y/n): "):
                targets.pop(nama_hapus, None)
                print(green(f"✅ Target '{nama_hapus}' dihapus."))
            else:
                print("Batal hapus.")
        elif pilih == "4":
            break
        else:
            print("❌ Pilihan tidak valid.")

# ========================
#  FITUR MENU & TRANSAKSI
# ========================

def pilih_sumber_saldo(user, action):
    while True:
        print("\n" + bold(cyan("💰 Pilih sumber saldo:")))
        print(f"{green('🏦')} 1. Saldo Utama")
        print(f"{magenta('🎯')} 2. Saldo Target")
        pilihan = input(bold("Pilih (1/2): ")).strip()
        if pilihan == "1":
            return "utama", None
        elif pilihan == "2":
            targets = users[user]["targets"]
            aktif = [name for name, d in targets.items() if d["status"] == "aktif"]
            if not aktif:
                print("❌ Tidak ada target aktif.")
                if konfirmasi_aksi("Gunakan saldo utama sebagai gantinya? (Y/n): "):
                    return "utama", None
                else:
                    return None, None
            print("Pilih target:")
            for i, n in enumerate(aktif, 1):
                t = targets[n]
                pct = int((t["saldo"] / t["target"]) * 100) if t["target"] > 0 else 0
                print(f"{i}. {n} → Rp {t['saldo']:,} / Rp {t['target']:,} ({pct}%)")
            sel = input("Masukkan nomor target: ").strip()
            if not sel.isdigit() or not (1 <= int(sel) <= len(aktif)):
                print("❌ Pilihan tidak valid.")
                continue
            chosen = aktif[int(sel)-1]
            return "target", chosen
        else:
            print("❌ Pilihan tidak valid.")

def nabung(user):
    print("\n" + bold(green("💸 NABUNG (UANG MASUK)")))
    sumber, target_name = pilih_sumber_saldo(user, "nabung")
    if sumber is None:
        return
    jumlah = input_nominal("Masukkan jumlah uang: Rp ")
    catatan = input_catatan()
    if sumber == "utama":
        users[user]["saldo_utama"] += jumlah
        users[user]["riwayat"].append([datetime.now().strftime("%Y-%m-%d %H:%M"), "nabung", jumlah, catatan])
        print(green("✅ Transaksi nabung ke saldo utama berhasil."))
        input("\nTekan Enter untuk kembali ke menu utama...")
        return
    else:
        tdata = users[user]["targets"].get(target_name)
        if not tdata:
            print("❌ Target tidak ditemukan.")
            input("\nTekan Enter untuk kembali ke menu utama...")
            return
        if tdata["status"] == "selesai":
            print("❌ Target sudah selesai, tidak bisa menambah lagi.")
            input("\nTekan Enter untuk kembali ke menu utama...")
            return
        tdata["saldo"] += jumlah
        tdata["riwayat"].append([datetime.now().strftime("%Y-%m-%d %H:%M"), "nabung", jumlah, catatan])
        if tdata["saldo"] >= tdata["target"]:
            tdata["saldo"] = tdata["target"]
            tdata["status"] = "selesai"
            print(bold(yellow(f"🎉 Target '{target_name}' telah tercapai!")))
        else:
            print(green(f"✅ Nabung ke target '{target_name}' berhasil. Saldo: Rp {tdata['saldo']:,}"))
        input("\nTekan Enter untuk kembali ke menu utama...")

def pengeluaran(user):
    print("\n" + bold(red("🧾 CATAT PENGELUARAN")))
    sumber, target_name = pilih_sumber_saldo(user, "keluar")
    if sumber is None:
        return

    jumlah = input_nominal("Masukkan jumlah pengeluaran: Rp ")
    catatan = input_catatan()
    saldo_utama = users[user]["saldo_utama"]
    now = datetime.now()
    last_withdraw = users[user].get("last_withdraw")

    # =====================
    # PENGELUARAN SALDO UTAMA
    # =====================
    if sumber == "utama":
        if last_withdraw and (now - last_withdraw).days < 365:
            sisa = 365 - (now - last_withdraw).days
            print(red(f"\n❌ Anda sudah melakukan penarikan tahun ini."))
            print(yellow(f"⏳ Coba lagi dalam {sisa} hari ({(last_withdraw + timedelta(days=365)).strftime('%d %B %Y')})."))
            input("\nTekan Enter untuk kembali ke menu utama...")
            return

        users[user]["last_withdraw"] = now

        if saldo_utama >= jumlah:
            users[user]["saldo_utama"] -= jumlah
            users[user]["riwayat"].append([datetime.now().strftime("%Y-%m-%d %H:%M"), "keluar", jumlah, catatan])
            print(green("\n✅ Pengeluaran dari saldo utama dicatat."))
        else:
            print(yellow("\n⚠️ Saldo utama tidak cukup."))
            users[user]["saldo_utama"] = int(saldo_utama * 0.3)
            users[user]["riwayat"].append([datetime.now().strftime("%Y-%m-%d %H:%M"), "keluar", jumlah, catatan])
            print(yellow("Saldo utama disesuaikan menjadi 30% dari saldo sebelumnya."))

        input("\nTekan Enter untuk kembali ke menu utama...")
        return

    # =====================
    # PENGELUARAN DARI TARGET
    # =====================
    tdata = users[user]["targets"].get(target_name)
    if not tdata:
        print(red("❌ Target tidak ditemukan."))
        input("\nTekan Enter untuk kembali ke menu utama...")
        return

    last_wd = tdata.get("last_withdraw")

    # Jika pernah tarik sebelumnya, hitung waktu tersisa
    if last_wd:
        delta = (now - last_wd).days
        if delta < 365:
            sisa_hari = 365 - delta
            next_tarik = last_wd + timedelta(days=365)
            print(red(f"\n❌ Anda sudah melakukan penarikan tahun ini untuk target ini."))
            print(yellow(f"⏳ Coba lagi dalam {sisa_hari} hari ({next_tarik.strftime('%d %B %Y')})."))
            input("\nTekan Enter untuk kembali ke menu utama...")
            return

    if tdata["saldo"] <= 0:
        print(red("❌ Saldo target kosong."))
        input("\nTekan Enter untuk kembali ke menu utama...")
        return

    max_tarik = int(tdata["saldo"] * 0.3)
    if max_tarik <= 0:
        print(red("❌ Saldo target tidak mencukupi untuk penarikan 30%."))
        input("\nTekan Enter untuk kembali ke menu utama...")
        return

    # Proses penarikan 30%
    tdata["saldo"] -= max_tarik
    tdata["last_withdraw"] = now
    tdata["riwayat"].append([datetime.now().strftime("%Y-%m-%d %H:%M"), "keluar", max_tarik, catatan])

    next_tarik = now + timedelta(days=365)

    print(green(f"\n✅ Penarikan 30% (Rp {max_tarik:,}) dari saldo target '{target_name}' berhasil."))
    print(yellow("⚠️ Anda hanya dapat melakukan penarikan 1x dalam setahun."))
    print(cyan(f"📅 Penarikan berikutnya dapat dilakukan pada: {next_tarik.strftime('%d %B %Y')} ({(next_tarik - now).days} hari lagi)."))

    input("\nTekan Enter untuk kembali ke menu utama...")

# ========================
#  FITUR LAIN (TIDAK DIUBAH)
# ========================

def lihat_saldo(user):
    print("\n" + bold(green("💰 SALDO & PROGRESS")))
    saldo = users[user]["saldo_utama"]
    targets = users[user]["targets"]
    print(f"{green('🏦')} Saldo Utama: Rp {saldo:,}")
    print("-" * 40)
    print(bold(magenta("🎯 Daftar Target:")))
    if not targets:
        print("(Belum ada target)")
    else:
        for tname, tdata in targets.items():
            t_target = tdata["target"]
            t_saldo = tdata["saldo"]
            pct = int((t_saldo / t_target) * 100) if t_target > 0 else 0
            if pct >= 100:
                pct = 100
                status = "✅ Selesai"
            else:
                status = "Aktif"
            bar_length = 20
            filled = int(bar_length * pct / 100)
            bar = "#" * filled + "-" * (bar_length - filled)
            print(f"{tname} → Rp {t_saldo:,} / Rp {t_target:,} ({pct}%) {status}")
            print(f"Progress: [{green(bar)}]")
    input("Tekan Enter untuk kembali...")

def lihat_riwayat(user):
    print("\n" + bold(cyan("📜 RIWAYAT TRANSAKSI")))
    print(bold("Pilih riwayat yang ingin dilihat:"))
    print(f"{green('🏦')} 1. Saldo Utama")
    print(f"{magenta('🎯')} 2. Riwayat Target")
    pil = input(bold("Pilih (1/2): ")).strip()

    if pil == "1":
        riwayat = users[user]["riwayat"]
        if not riwayat:
            print("Belum ada transaksi pada saldo utama.")
            input("Tekan Enter untuk kembali...")
            return
        print("-" * 80)
        print(f"{'Tanggal':<20} | {'Tipe':<10} | {'Jumlah (Rp)':>12} | {'Catatan':<30}")
        print("-" * 80)
        for tgl, tipe, jumlah, catatan in riwayat:
            print(f"{tgl:<20} | {tipe:<10} | {jumlah:>12,} | {catatan:<30}")
        print("-" * 80)
        input("Tekan Enter untuk kembali...")

    elif pil == "2":
        targets = users[user]["targets"]
        if not targets:
            print("Belum ada target.")
            input("Tekan Enter untuk kembali...")
            return

        print("Pilih target untuk melihat riwayat:")
        names = list(targets.keys())
        for i, n in enumerate(names, 1):
            print(f"{i}. {n}")
        sel = input("Masukkan nomor target: ").strip()
        if not sel.isdigit() or not (1 <= int(sel) <= len(names)):
            print("❌ Pilihan tidak valid.")
            input("Tekan Enter untuk kembali...")
            return

        chosen = names[int(sel)-1]
        ri = targets[chosen]["riwayat"]
        if not ri:
            print(f"Belum ada transaksi pada target '{chosen}'.")
            input("Tekan Enter untuk kembali...")
            return

        print(f"--- Riwayat Target: {chosen} ---")
        print("-" * 80)
        print(f"{'Tanggal':<20} | {'Tipe':<10} | {'Jumlah (Rp)':>12} | {'Catatan':<30}")
        print("-" * 80)
        for tgl, tipe, jumlah, catatan in ri:
            print(f"{tgl:<20} | {tipe:<10} | {jumlah:>12,} | {catatan:<30}")
        print("-" * 80)
        input("Tekan Enter untuk kembali...")

    else:
        print("Pilihan tidak valid.")
        input("Tekan Enter untuk kembali...")


def analisis_keuangan(user):
    print("\n" + bold(yellow("📊 ANALISIS KEUANGAN")))
    total_nabung = sum(j[2] for j in users[user]["riwayat"] if j[1] == "nabung")
    total_keluar = sum(j[2] for j in users[user]["riwayat"] if j[1] == "keluar")

    for t in users[user]["targets"].values():
        total_nabung += sum(tx[2] for tx in t["riwayat"] if tx[1] == "nabung")
        total_keluar += sum(tx[2] for tx in t["riwayat"] if tx[1] == "keluar")

    if total_nabung == 0:
        print("Belum ada data tabungan.")
        input("Tekan Enter untuk kembali...")
        return

    rasio = (total_keluar / total_nabung) * 100
    if rasio < 30:
        status = green("Dompet Sehat 😎")
    elif 30 <= rasio <= 60:
        status = yellow("Keuangan Cukup Stabil 🙂")
    else:
        status = red("Boros Banget 😭")

    print(f"Total Nabung: Rp {total_nabung:,}")
    print(f"Total Pengeluaran: Rp {total_keluar:,}")
    print(f"Rasio Pengeluaran: {rasio:.2f}%")
    print(f"Status: {status}")
    input("Tekan Enter untuk kembali...")


def backup_data(user):
    filename = f"{users[user]['username']}_backup.csv"
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Tanggal", "Tipe", "Jumlah", "Catatan", "Sumber"])
        for row in users[user]["riwayat"]:
            writer.writerow([row[0], row[1], row[2], row[3], "utama"])
        for tname, tdata in users[user]["targets"].items():
            for row in tdata["riwayat"]:
                writer.writerow([row[0], row[1], row[2], row[3], f"target:{tname}"])
    print(green(f"✅ Data berhasil dibackup ke {filename}"))

def menu_utama(user):
    while True:
        clear()
        print(bold(cyan("="*50)))
        print(bold(yellow("� ChillFinance - Nabung Gen Z")))
        print(bold(cyan("="*50)))
        print(f"👋 Halo, {bold(users[user]['username'])}")
        print(f"{green('1️⃣')} Lihat Saldo & Target")
        print(f"{green('2️⃣')} Nabung")
        print(f"{red('3️⃣')} Pengeluaran")
        print(f"{magenta('4️⃣')} Kelola Target")
        print(f"{cyan('5️⃣')} Lihat Riwayat")
        print(f"{yellow('6️⃣')} Analisis Keuangan")
        print(f"{green('7️⃣')} Backup Data")
        print(f"{red('8️⃣')} Logout")

        pilih = input(bold("Pilih menu: ")).strip()

        match pilih:
            case "1":
                lihat_saldo(user)

            case "2":
                nabung(user)

            case "3":
                pengeluaran(user)

            case "4":
                set_target(user)

            case "5":
                lihat_riwayat(user)

            case "6":
                analisis_keuangan(user)

            case "7":
                if konfirmasi_aksi("Backup data sekarang? (Y/n): "):
                    backup_data(user)

            case "8":
                if konfirmasi_aksi("Yakin ingin logout? (Y/n): "):
                    print("Logout berhasil.")
                    time.sleep(1)
                    return

            case _:
                print(red("❌ Pilihan tidak valid."))

# ========================
#  MAIN
# ========================

def main():
    while True:
        clear()
        print(bold(cyan("💸 ChillFinance - Nabung Gen Z")))
        print(bold(""))
        print(f"{green('1️⃣')} Login")
        print(f"{yellow('2️⃣')} Register")
        print(f"{red('3️⃣')} Keluar")
        pilih = input(bold("Pilih menu: ")).strip()
        if pilih == "1":
            user = login()
            menu_utama(user)
        elif pilih == "2":
            user = register()
            menu_utama(user)
        elif pilih == "3":
            if konfirmasi_aksi("Yakin keluar dari aplikasi? (Y/n): "):
                print("Sampai jumpa!")
                sys.exit()
        else:
            print(red("❌ Pilihan tidak valid."))

if __name__ == "__main__":
    main()