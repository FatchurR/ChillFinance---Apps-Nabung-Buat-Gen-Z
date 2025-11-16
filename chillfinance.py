import csv
import os
import sys
import time
from datetime import datetime, timedelta
from getpass import getpass

# =========================================================
#              🔥 CHILLFINANCE SMOOTH ENGINE 🔥
# =========================================================

def supports_ansi():
    if os.name == "nt":
        return "WT_SESSION" in os.environ or "ANSICON" in os.environ
    return True

USE_ANSI = supports_ansi()

def smooth_print(text, delay=0.0015):
    for c in text:
        sys.stdout.write(c)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def smooth_replace(line):
    sys.stdout.write("\r" + " " * 250 + "\r")
    sys.stdout.write(line)
    sys.stdout.flush()

def smooth_clear():
    if not USE_ANSI:
        return
    for _ in range(2):
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.flush()
        time.sleep(0.008)

_original_clear = None
def patch_clear_function(original_clear_func):
    global _original_clear
    _original_clear = original_clear_func
    def new_clear():
        smooth_clear()
        original_clear_func()
    return new_clear

def animate_digit(digit):
    if not USE_ANSI:
        return
    sys.stdout.write(f"\033[1m{digit}\033[0m")
    sys.stdout.flush()
    time.sleep(0.01)

def render_input(prompt, angka_str, formatter):
    smooth_replace(prompt + formatter(angka_str))

def patch_input_nominal(input_nominal_func, formatter):
    def wrapper(prompt):
        original_write = sys.stdout.write

        def patched_write(s):
            if len(s) == 1 and s.isdigit():
                animate_digit(s)
            original_write(s)

        sys.stdout.write = patched_write
        try:
            result = input_nominal_func(prompt)
        finally:
            sys.stdout.write = original_write

        return result
    return wrapper

# =========================================================
#  UTILITAS & VALIDASI
# =========================================================

def _original_clear_func():
    os.system('cls' if os.name == 'nt' else 'clear')

clear = patch_clear_function(_original_clear_func)

def color(text, code):
    if not USE_ANSI:
        return text
    return f"\033[{code}m{text}\033[0m"

def bold(text):
    if not USE_ANSI:
        return text
    return f"\033[1m{text}\033[0m"

def cyan(t): return color(t, '36')
def green(t): return color(t, '32')
def yellow(t): return color(t, '33')
def red(t): return color(t, '31')
def magenta(t): return color(t, '35')

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

# =========================================================
#  FORMAT RUPIAH
# =========================================================

def format_rupiah(angka):
    try:
        angka = float(angka)
        return f"{angka:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "0,00"

def parse_nominal_input(teks):
    return int(''.join(ch for ch in teks if ch.isdigit()))

def format_rupiah_input(angka_str):
    if not angka_str:
        return ""
    try:
        return format_rupiah(int(angka_str))
    except:
        return ""

# =========================================================
#  INPUT NOMINAL CROSS PLATFORM + SMOOTH
# =========================================================

if os.name == "nt":
    import msvcrt
else:
    import termios
    import tty

def input_nominal(prompt):
    MAX_NOMINAL = 1_000_000_000_000
    print(prompt, end='', flush=True)

    angka_str = ""
    warning_shown = False

    # =============== WINDOWS ===============
    if os.name == "nt":
        while True:
            ch = msvcrt.getwch()

            # ENTER
            if ch == '\r':
                print()
                if not angka_str:
                    print("❌ Nominal tidak boleh kosong.")
                    print(prompt, end='', flush=True)
                    angka_str = ""
                    warning_shown = False
                    continue

                val = parse_nominal_input(angka_str)
                if val <= 0:
                    print("❌ Nominal harus lebih dari 0.")
                    print(prompt, end='', flush=True)
                    angka_str = ""
                    continue

                if val > MAX_NOMINAL:
                    print(f"❌ Batas maksimum Rp {format_rupiah(MAX_NOMINAL)}")
                    print(prompt, end='', flush=True)
                    angka_str = ""
                    continue

                print(f"Nominal diterima: Rp {format_rupiah(val)}")
                return val

            # BACKSPACE
            elif ch == '\b':
                if angka_str:
                    angka_str = angka_str[:-1]
                    render_input(prompt, angka_str, format_rupiah_input)

            # DIGIT
            elif ch.isdigit():
                new_str = angka_str + ch
                val = parse_nominal_input(new_str)

                if val > MAX_NOMINAL:
                    if not warning_shown:
                        print("\n⚠️ Maksimal tercapai")
                        print(prompt + format_rupiah_input(angka_str), end="", flush=True)
                        warning_shown = True
                    continue

                angka_str = new_str
                render_input(prompt, angka_str, format_rupiah_input)

            continue

    # =============== LINUX / MAC ===============
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        while True:
            ch = sys.stdin.read(1)

            # ENTER
            if ch in ('\n', '\r'):
                print()
                if not angka_str:
                    print("❌ Nominal tidak boleh kosong.")
                    print(prompt, end='', flush=True)
                    angka_str = ""
                    continue

                val = parse_nominal_input(angka_str)
                if val <= 0:
                    print("❌ Nominal harus lebih dari 0.")
                    print(prompt, end='', flush=True)
                    angka_str = ""
                    continue

                if val > MAX_NOMINAL:
                    print(f"❌ Batas maksimum Rp {format_rupiah(MAX_NOMINAL)}")
                    print(prompt, end='', flush=True)
                    angka_str = ""
                    continue

                print(f"Nominal diterima: Rp {format_rupiah(val)}")
                return val

            # BACKSPACE
            elif ch == '\x7f':
                if angka_str:
                    angka_str = angka_str[:-1]
                    render_input(prompt, angka_str, format_rupiah_input)

            # DIGIT
            elif ch.isdigit():
                new_str = angka_str + ch
                val = parse_nominal_input(new_str)

                if val > MAX_NOMINAL:
                    if not warning_shown:
                        print("\n⚠️ Maksimal tercapai")
                        print(prompt + format_rupiah_input(angka_str), end="", flush=True)
                        warning_shown = True
                    continue

                angka_str = new_str
                render_input(prompt, angka_str, format_rupiah_input)

    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

# =========================================================
#  STRUKTUR DATA
# =========================================================
users = {}

# =========================================================
#  AUTENTIKASI (REGISTER & LOGIN)
# =========================================================

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

    print(green("✅ Registrasi berhasil!"))
    input("Tekan Enter untuk login...")
    return login()


def login():
    clear()
    print(bold(cyan("🔑 LOGIN")))
    uname = input("Username: ").strip().lower()
    pw = getpass("Password: ")

    if uname not in users or users[uname]["password"] != pw:
        print("❌ Username atau password salah.")
        input("Enter untuk ulangi...")
        return login()

    print(green(f"✅ Selamat datang, {users[uname]['username']}!"))
    time.sleep(0.8)
    return uname


# =========================================================
#  MENU TARGET TABUNGAN
# =========================================================

def set_target(user):
    while True:
        clear()
        print(bold(magenta("🎯 KELOLA TARGET TABUNGAN")))
        print(f"{green('➕')} 1. Tambah Target Baru")
        print(f"{cyan('📋')} 2. Lihat Daftar Target")
        print(f"{red('🗑️')} 3. Hapus Target")
        print(f"{yellow('↩️')} 4. Kembali")

        pilih = input(bold("Pilih: ")).strip()

        # ================= TAMBAH TARGET =================
        if pilih == "1":
            clear()
            print(bold(magenta("➕ TAMBAH TARGET BARU")))
            nama = input("Nama Target (unik): ").strip()

            if not nama:
                print(red("❌ Nama target tidak boleh kosong."))
                input("Enter...")
                continue

            key = nama.lower()
            if any(k.lower() == key for k in users[user]["targets"]):
                print(red("❌ Target dengan nama tersebut sudah ada."))
                input("Enter...")
                continue

            target_amt = input_nominal("Masukkan nominal target: Rp ")

            users[user]["targets"][nama] = {
                "target": target_amt,
                "saldo": 0,
                "status": "aktif",
                "riwayat": [],
                "last_withdraw": None
            }
            print(green(f"✅ Target '{nama}' berhasil dibuat."))
            input("Enter...")

        # ================= LIHAT TARGET =================
        elif pilih == "2":
            clear()
            print(bold(cyan("📋 DAFTAR TARGET")))
            targets = users[user]["targets"]

            if not targets:
                print("(Belum ada target)")
                input("Enter...")
                continue

            for idx, (tname, tdata) in enumerate(targets.items(), 1):
                t_target = tdata["target"]
                t_saldo = tdata["saldo"]

                pct = int((t_saldo / t_target) * 100) if t_target else 0
                pct = min(pct, 100)

                bar_len = 20
                filled = int(bar_len * pct / 100)
                bar = "#" * filled + "-" * (bar_len - filled)

                status = "✅ Selesai" if pct == 100 else "Aktif"

                print(f"{idx}. {tname} → Rp {t_saldo:,} / Rp {format_rupiah(t_target)}  ({pct}%) {status}")
                print(f"    [{green(bar)}]")

            input("Enter...")

        # ================= HAPUS TARGET =================
        elif pilih == "3":
            clear()
            targets = users[user]["targets"]

            if not targets:
                print("Tidak ada target untuk dihapus.")
                input("Enter...")
                continue

            print(bold(red("🗑️ HAPUS TARGET")))
            names = list(targets.keys())

            for i, n in enumerate(names, 1):
                print(f"{i}. {n}")

            sel = input("Masukkan nomor target: ").strip()

            if not sel.isdigit() or not (1 <= int(sel) <= len(names)):
                print("❌ Pilihan tidak valid.")
                input("Enter...")
                continue

            nama_hapus = names[int(sel) - 1]

            konfir = input(f"Yakin hapus '{nama_hapus}'? (Y/n): ").lower()
            if konfir in ("y", ""):
                targets.pop(nama_hapus)
                print(green("✅ Target berhasil dihapus."))
            else:
                print(yellow("Dibatalkan."))

            input("Enter...")

        elif pilih == "4":
            break

        else:
            print(red("❌ Pilihan tidak valid."))
            input("Enter...")


# =========================================================
#  PILIH SUMBER SALDO
# =========================================================

def pilih_sumber_saldo(user, action):
    while True:
        clear()
        print(bold(cyan("💰 PILIH SUMBER SALDO")))
        print("1. Saldo Utama")
        print("2. Saldo Target")

        pilihan = input("Pilih (1/2): ").strip()

        if pilihan == "1":
            return "utama", None

        elif pilihan == "2":
            targets = users[user]["targets"]
            aktif = [name for name, d in targets.items() if d["status"] == "aktif"]

            if not aktif:
                print(red("❌ Tidak ada target aktif."))
                if input("Gunakan saldo utama saja? (Y/n): ").lower() in ("y", ""):
                    return "utama", None
                return None, None

            print("Pilih target:")
            for i, n in enumerate(aktif, 1):
                t = targets[n]
                pct = int((t["saldo"] / t["target"]) * 100)
                print(f"{i}. {n} → Rp {t['saldo']:,} ({pct}%)")

            sel = input("Nomor: ").strip()
            if sel.isdigit() and 1 <= int(sel) <= len(aktif):
                return "target", aktif[int(sel) - 1]

            print(red("❌ Pilihan tidak valid."))
            input("Enter...")

        else:
            print(red("❌ Pilihan tidak valid."))
            input("Enter...")


# =========================================================
#  FITUR NABUNG
# =========================================================

def nabung(user):
    clear()
    print(bold(green("💸 NABUNG UANG")))

    sumber, target_name = pilih_sumber_saldo(user, "nabung")
    if sumber is None:
        return

    jumlah = input_nominal("Masukkan jumlah uang: Rp ")
    catatan = input("Catatan (opsional): ").strip() or "-"

    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    if sumber == "utama":
        users[user]["saldo_utama"] += jumlah
        users[user]["riwayat"].append([now, "nabung", jumlah, catatan])
        print(green("✅ Nabung ke saldo utama berhasil!"))
        input("Enter...")
        return

    tdata = users[user]["targets"][target_name]
    tdata["saldo"] += jumlah
    tdata["riwayat"].append([now, "nabung", jumlah, catatan])

    if tdata["saldo"] >= tdata["target"]:
        tdata["saldo"] = tdata["target"]
        tdata["status"] = "selesai"
        print(yellow(f"🎉 Target '{target_name}' telah tercapai!"))
    else:
        print(green(f"✅ Nabung ke '{target_name}' berhasil."))

    input("Enter...")


# =========================================================
#  FITUR PENGELUARAN
# =========================================================

def pengeluaran(user):
    clear()
    print(bold(red("🧾 CATAT PENGELUARAN")))

    sumber, target_name = pilih_sumber_saldo(user, "keluar")
    if sumber is None:
        return

    jumlah = input_nominal("Masukkan jumlah pengeluaran: Rp ")
    catatan = input("Catatan (opsional): ").strip() or "-"
    now = datetime.now()

    # ------- SALDO UTAMA -------
    if sumber == "utama":
        saldo = users[user]["saldo_utama"]

        if jumlah > saldo:
            print(yellow("⚠️ Saldo tidak cukup, semua saldo akan digunakan."))
            jumlah = saldo

        users[user]["saldo_utama"] -= jumlah
        users[user]["riwayat"].append([now.strftime("%Y-%m-%d %H:%M"), "keluar", jumlah, catatan])

        print(green("✅ Pengeluaran berhasil dicatat."))
        input("Enter...")
        return

    # ------- SALDO TARGET -------
    tdata = users[user]["targets"][target_name]

    if tdata["saldo"] <= 0:
        print(red("❌ Saldo target kosong."))
        input("Enter...")
        return

    last_wd = tdata["last_withdraw"]
    if last_wd:
        delta = (now - last_wd).days
        if delta < 365:
            print(red("❌ Sudah melakukan penarikan tahun ini."))
            print(yellow(f"Coba lagi dalam {365-delta} hari."))
            input("Enter...")
            return

    max_tarik = int(tdata["saldo"] * 0.3)
    if max_tarik <= 0:
        print(red("❌ Saldo tidak mencukupi untuk penarikan 30%."))
        input("Enter...")
        return

    print(yellow("⚠️ Penarikan target hanya 1x setahun"))
    print(cyan(f"Total yang akan ditarik: Rp {format_rupiah(max_tarik)}"))

    if input("Lanjutkan? (Y/n): ").lower() not in ("y", ""):
        print("❌ Dibatalkan.")
        input("Enter...")
        return

    tdata["saldo"] -= max_tarik
    tdata["last_withdraw"] = now
    tdata["riwayat"].append([now.strftime("%Y-%m-%d %H:%M"), "keluar", max_tarik, catatan])

    print(green("✅ Penarikan berhasil!"))
    print(cyan(f"Bisa tarik lagi: { (now + timedelta(days=365)).strftime('%d %B %Y') }"))
    input("Enter...")


# =========================================================
#  LIHAT SALDO
# =========================================================

def lihat_saldo(user):
    clear()
    print(bold(green("💰 SALDO & PROGRESS")))
    saldo = users[user]["saldo_utama"]
    targets = users[user]["targets"]

    print(f"🏦 Saldo Utama: Rp {format_rupiah(saldo)}")
    print("-" * 40)

    print(bold(magenta("🎯 TARGET TABUNGAN")))
    if not targets:
        print("(Belum ada target)")
    else:
        for tname, tdata in targets.items():
            t_target = tdata["target"]
            t_saldo = tdata["saldo"]

            pct = int((t_saldo / t_target) * 100) if t_target else 0
            pct = min(pct, 100)

            bar_len = 20
            filled = int(bar_len * pct / 100)
            bar = "#" * filled + "-" * (bar_len - filled)

            status = "🎉 Selesai" if pct == 100 else "Aktif"

            print(f"{tname} → Rp {t_saldo:,} / Rp {format_rupiah(t_target)}  ({pct}%) {status}")
            print(f"    [{green(bar)}]")

    input("Enter...")


# =========================================================
#  LIHAT RIWAYAT TRANSAKSI
# =========================================================

def lihat_riwayat(user):
    while True:
        clear()
        print(bold(cyan("📜 RIWAYAT TRANSAKSI")))
        print("1. Saldo Utama")
        print("2. Riwayat Target")
        print("3. Kembali")

        pil = input("Pilih: ").strip()

        # ====== Saldo Utama ======
        if pil == "1":
            clear()
            riw = users[user]["riwayat"]

            if not riw:
                print("Belum ada transaksi.")
                input("Enter...")
                continue

            print("-" * 80)
            print(f"{'Tanggal':<20} | {'Tipe':<10} | {'Jumlah':>15} | {'Catatan':<30}")
            print("-" * 80)

            for t, tipe, jml, cat in riw:
                print(f"{t:<20} | {tipe:<10} | {jml:>15,} | {cat:<30}")

            print("-" * 80)
            input("Enter...")

        # ====== Target ======
        elif pil == "2":
            clear()
            targets = users[user]["targets"]

            if not targets:
                print("Belum ada target.")
                input("Enter...")
                continue

            print("Pilih target:")
            names = list(targets.keys())

            for i, n in enumerate(names, 1):
                print(f"{i}. {n}")

            sel = input("Nomor: ").strip()
            if not sel.isdigit() or not (1 <= int(sel) <= len(names)):
                print("❌ Pilihan tidak valid.")
                input("Enter...")
                continue

            chosen = names[int(sel) - 1]
            ri = targets[chosen]["riwayat"]

            clear()
            if not ri:
                print("Belum ada transaksi.")
                input("Enter...")
                continue

            print(f"--- Riwayat Target: {chosen} ---")
            print("-" * 80)
            print(f"{'Tanggal':<20} | {'Tipe':<10} | {'Jumlah':>15} | {'Catatan':<30}")
            print("-" * 80)

            for t, tipe, jml, cat in ri:
                print(f"{t:<20} | {tipe:<10} | {jml:>15,} | {cat:<30}")

            print("-" * 80)
            input("Enter...")

        elif pil == "3":
            break

        else:
            print(red("❌ Pilihan tidak valid."))
            input("Enter...")


# =========================================================
#  ANALISIS KEUANGAN
# =========================================================

def analisis_keuangan(user):
    clear()
    print(bold(yellow("📊 ANALISIS KEUANGAN")))

    total_nabung = sum(j[2] for j in users[user]["riwayat"] if j[1] == "nabung")
    total_keluar = sum(j[2] for j in users[user]["riwayat"] if j[1] == "keluar")

    for t in users[user]["targets"].values():
        total_nabung += sum(r[2] for r in t["riwayat"] if r[1] == "nabung")
        total_keluar += sum(r[2] for r in t["riwayat"] if r[1] == "keluar")

    if total_nabung == 0:
        print("Belum ada data tabungan.")
        input("Enter...")
        return

    rasio = (total_keluar / total_nabung) * 100

    if rasio < 30:
        status = green("Dompet Sehat 😎")
    elif rasio <= 60:
        status = yellow("Keuangan Cukup Stabil 🙂")
    else:
        status = red("Boros Banget 😭")

    print(f"Total Nabung      : Rp {format_rupiah(total_nabung)}")
    print(f"Total Pengeluaran : Rp {format_rupiah(total_keluar)}")
    print(f"Rasio Pengeluaran : {rasio:.2f}%")
    print(f"Status            : {status}")

    input("Enter...")


# =========================================================
#  BACKUP CSV
# =========================================================

def backup_data(user):
    clear()
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
    input("Enter...")

# =========================================================
#  MENU UTAMA
# =========================================================

def menu_utama(user):
    while True:
        clear()
        print(bold(cyan("=" * 50)))
        print(bold(yellow("💸 ChillFinance - Nabung Gen Z by FatchurR")))
        print(bold(cyan("=" * 50)))
        print(f"👋 Halo, {bold(users[user]['username'])}")
        print()
        print("1️⃣  Lihat Saldo & Target")
        print("2️⃣  Nabung")
        print("3️⃣  Pengeluaran")
        print("4️⃣  Kelola Target")
        print("5️⃣  Lihat Riwayat")
        print("6️⃣  Analisis Keuangan")
        print("7️⃣  Backup Data")
        print("8️⃣  Logout")

        pilih = input("\nPilih menu: ").strip()

        if pilih == "1":
            lihat_saldo(user)
        elif pilih == "2":
            nabung(user)
        elif pilih == "3":
            pengeluaran(user)
        elif pilih == "4":
            set_target(user)
        elif pilih == "5":
            lihat_riwayat(user)
        elif pilih == "6":
            analisis_keuangan(user)
        elif pilih == "7":
            if input("Backup data sekarang? (Y/n): ").lower() in ("y", ""):
                backup_data(user)
        elif pilih == "8":
            if input("Yakin ingin logout? (Y/n): ").lower() in ("y", ""):
                print("Logout berhasil. Sampai jumpa! 👋")
                time.sleep(1)
                break
        else:
            print(red("❌ Pilihan tidak valid."))
            input("Enter untuk lanjut...")


# =========================================================
#  MAIN PROGRAM (AUTH MENU)
# =========================================================

def main():
    while True:
        clear()
        print(bold(cyan("💸 ChillFinance - Nabung Gen Z")))
        print()
        print("1️⃣  Login")
        print("2️⃣  Register")
        print("3️⃣  Keluar")

        pilih = input("\nPilih menu: ").strip()

        if pilih == "1":
            user = login()
            menu_utama(user)

        elif pilih == "2":
            user = register()
            menu_utama(user)

        elif pilih == "3":
            konfirmasi = input("Yakin keluar dari aplikasi? (Y/n): ").lower()
            if konfirmasi in ("y", ""):
                print("Sampai jumpa! 👋")
                time.sleep(0.8)
                sys.exit()
        else:
            print(red("❌ Pilihan tidak valid."))
            input("Enter untuk lanjut...")


# =========================================================
#  PATCH SMOOTH INPUT NOMINAL
# =========================================================

# Pasang "smooth engine" untuk input_nominal (animasi digit & anti-flicker)
input_nominal = patch_input_nominal(input_nominal, format_rupiah_input)


# =========================================================
#  ENTRY POINT
# =========================================================

if __name__ == "__main__":
    main()

