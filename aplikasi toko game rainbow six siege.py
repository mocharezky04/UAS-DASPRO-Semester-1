import json
import os
import pwinput
import time
from datetime import datetime
from prettytable import PrettyTable

# Nama file JSON
DATABASE_FILE = r"C:\Users\Acer\Documents\Kerjaan\kuliah\dp\UAS semester 1\Database aplikasi toko.json"

# Fungsi untuk memuat database
def muat_database():
    if not os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, 'w') as f:
            json.dump({"users": {}, "items": {}, "vouchers": {}}, f)
    with open(DATABASE_FILE, 'r') as f:
        return json.load(f)

# Fungsi untuk menyimpan database
def simpan_database(data):
    with open(DATABASE_FILE, 'w') as f:
        json.dump(data, f, indent=3)

# Fungsi untuk membersihkan layar
def bersihkan_layar():
    os.system('cls' if os.name == 'nt' else 'clear')

# Fungsi untuk menentukan waktu saat ini
def waktu_sekarang():
    jam = datetime.now().hour
    if 1 <= jam < 12:
        return "Pagi"
    elif 12 <= jam < 18:
        return "Siang"
    else:
        return "Malam"

# Fungsi untuk login
def login(data):
    bersihkan_layar()
    print("=== Login ===")
    while True:
        username = input("Username: ").strip()
        if username not in data["users"]:
            print("Username tidak ditemukan! Silahkan coba lagi.")
        elif data["users"][username].get("locked", False):
            print(f"Akun {username} sudah terkunci. Silahkan hubungi admin.\n")
            time.sleep(3)
            return None 
        else:
            print(f"Selamat datang, {username}!\n")
            break
    for percobaan in range(3):
        password = pwinput.pwinput("Password: ").strip()
        if data["users"][username]["password"] == password:
            print("Login berhasil!\n")
            return username
        else:
            sisa_percobaan = 2 - percobaan
            print(f"Password salah! Percobaan tersisa: {sisa_percobaan}")
    
    print(f"Akun {username} telah terkunci. Silahkan hubungi admin untuk membuka kunci.\n")
    data["users"][username]["locked"] = True
    simpan_database(data)
    time.sleep(3)
    return None

# Fungsi untuk mendaftar member baru
def daftar_pengguna(data):
    bersihkan_layar()
    print("=== Daftar Member Baru ===")
    while True:
        username = input("Masukkan username: ").strip()
        if not username:
            print("Username tidak boleh kosong!")
        elif username in data["users"]:
            print("Username sudah terdaftar!")
        else:
            break
    while True:
        password = pwinput.pwinput("Masukkan password: ").strip()
        if not password:
            print("Password tidak boleh kosong!")
        else:
            break
    data["users"][username] = {
        "password": password,
        "tipe_member": "biasa",
        "saldo": 100000,
        "vouchers": ["WELCOME100"],
        "pembelian": []
    }
    print(f"Member berhasil didaftarkan! Anda mendapat 1 voucher WELCOME100.\n")
    time.sleep(3)
    simpan_database(data)

# Fungsi untuk menampilkan barang
def tampilkan_barang(tipe_member, data):
    bersihkan_layar()
    waktu = waktu_sekarang()
    print(f"=== Barang yang Tersedia Toko, {waktu} ===")
    barang = data["items"][waktu]
    table = PrettyTable(["No", "Nama Barang", "Harga"])

    vip_only_items = [
        "Skin Black Ice",  "Skin Toolbox", "Skin Skull Rain",
        "Skin Rod Reel", "Skin La Clave", "Skin Piranha"
    ]
    for key, (nama, harga) in barang.items():
        if tipe_member == "biasa" and nama in vip_only_items:
            continue
        table.add_row([key, nama, f"Rp {harga:,}"])
    
    print(table)

# Fungsi untuk memvalidasi dan menggunakan voucher
def gunakan_voucher(kode_voucher, username, data):
    user_data = data["users"][username]
    if kode_voucher not in data["vouchers"]:
        print("Voucher tidak valid!")
        return 0

    voucher_data = data["vouchers"][kode_voucher]

    if kode_voucher not in user_data["vouchers"]:
        print("Voucher sudah digunakan atau tidak dimiliki!")
        return 0

    hari_ini = datetime.now().strftime("%Y-%m-%d")
    if hari_ini > voucher_data["valid_sampai"]:
        print("Voucher sudah kedaluwarsa!")
        return 0

    # Hapus voucher setelah digunakan
    user_data["vouchers"].remove(kode_voucher)
    print(f"Voucher {kode_voucher} digunakan! Diskon sebesar {voucher_data['diskon']}% diterapkan.")
    simpan_database(data)  
    return voucher_data["diskon"]

# Fungsi untuk membeli barang
def beli_barang(username, data):
    bersihkan_layar()
    user_data = data["users"][username]
    waktu = waktu_sekarang()
    barang = data["items"][waktu]
    tampilkan_barang(user_data["tipe_member"], data)
    pilihan = input("Masukkan nomor barang yang ingin dibeli (0 untuk batal): ").strip()
    if pilihan == "0":
        print("Pembelian dibatalkan.")
        return

    if pilihan not in barang:
        print("Pilihan tidak valid!")
        return

    nama, harga = barang[pilihan]
    if nama == "Skin Black Ice" and user_data["tipe_member"] == "biasa":
        print("Barang ini hanya tersedia untuk member VIP.")
        return

    if user_data["saldo"] < harga:
        print("Saldo Anda tidak mencukupi!")
        return

    # Gunakan voucher
    diskon = 0
    if user_data["vouchers"]:
        while True:
            gunakan = input("Apakah Anda ingin menggunakan voucher? (y/n): ").strip().lower()
            if gunakan == "y":
                print("Voucher tersedia:", user_data["vouchers"])
                kode_voucher = input("Masukkan kode voucher: ").strip().upper()
                diskon = gunakan_voucher(kode_voucher, username, data)
            elif gunakan == "n":
                print("Voucher tidak digunakan.")
            else:
                print("Input tidak valid. Silahkan coba lagi.")
            if gunakan in ["y", "n"]:
                break

    # Hitung total harga dengan diskon
    if diskon > 0:
        harga_diskon = harga - (harga * diskon / 100)
    else:
        harga_diskon = harga

    if user_data["saldo"] >= harga_diskon:
        user_data["saldo"] -= harga_diskon
        user_data["pembelian"].append((nama, harga_diskon))
        print(f"Pembelian berhasil! Anda membeli {nama} seharga Rp {harga_diskon:,}.")
        simpan_database(data)
    else:
        print("Saldo tidak mencukupi setelah diskon!")

# Fungsi untuk melakukan top-up saldo
def top_up_saldo(username, data):
    bersihkan_layar()
    user_data = data["users"][username]
    print("=== Top-Up Saldo ===")
    print(f"Saldo Anda saat ini: Rp {user_data['saldo']:,}")
    try:
        jumlah_top_up = int(input("Masukkan jumlah top-up: ").strip())
        if jumlah_top_up <= 0:
            print("Jumlah top-up harus lebih dari 0!")
            return
        user_data["saldo"] += jumlah_top_up
        print(f"Top-up berhasil! Saldo Anda sekarang: Rp {user_data['saldo']:,}")
        simpan_database(data)
    except ValueError:
        print("Input tidak valid! Masukkan angka yang benar.")

def tampilkan_riwayat_pembelian(username, data):
    bersihkan_layar()
    user_data = data["users"][username]
    print("=== Riwayat Pembelian ===")
    if not user_data["pembelian"]:
        print("Belum ada riwayat pembelian.")
    else:
        table = PrettyTable(["Nama Barang", "Harga"])
        for nama, harga in user_data["pembelian"]:
            table.add_row([nama, f"Rp {harga:,}"])
        print(table)

def upgrade_ke_vip(username, data):
    bersihkan_layar()
    user_data = data["users"][username]
    if user_data["tipe_member"] == "vip":
        print("Anda sudah menjadi member VIP.")
        return

    biaya_upgrade = 350000
    print(f"Biaya untuk upgrade ke member VIP adalah Rp {biaya_upgrade:,}.")
    while True:
        konfirmasi = input("Apakah Anda yakin ingin upgrade ke member VIP? (y/n): ").strip().lower()
        if konfirmasi == "y":
            if user_data["saldo"] >= biaya_upgrade:
                user_data["saldo"] -= biaya_upgrade
                user_data["tipe_member"] = "vip"
                user_data["vouchers"].append("VIP100")
                user_data["vouchers"].append("VIP200")
                print("Upgrade ke VIP berhasil! Selamat anda bisa membeli barang khusus VIP dan bisa Menggunakan kode voucher baru anda yaitu VIP100 dan VIP200.")
                simpan_database(data)
            else:
                print("Saldo Anda tidak mencukupi untuk upgrade ke VIP.")
        elif konfirmasi == "n":
            print("Upgrade ke VIP dibatalkan.")
        else:
            print("Input tidak valid. Silahkan coba lagi.")
        if konfirmasi in ["y", "n"]:
            break

# Fungsi untuk menampilkan menu utama
def menu_utama(username, data):
    while True:
        try:
            bersihkan_layar()
            user_data = data["users"][username]
            waktu_ini = waktu_sekarang() + datetime.now().strftime("\n%H:%M:%S")
            print(f"Selamat datang, {username} ({user_data['tipe_member'].capitalize()})")
            print("Saldo Anda:", f"Rp {user_data['saldo']:,}")
            print("Voucher Anda:", user_data["vouchers"])
            print(f"Waktu saat ini: {waktu_ini}")
            print("\nMenu:")
            print("1. Tampilkan barang")
            print("2. Beli barang")
            print("3. Tampilkan riwayat pembelian")
            print("4. Upgrade ke VIP")
            print("5. Top-Up Saldo")
            print("0. Keluar")

            pilihan = input("\nPilih menu: ").strip()

            if pilihan == "1":
                tampilkan_barang(user_data["tipe_member"], data)
                input("\nTekan Enter untuk kembali ke menu...")
            elif pilihan == "2":
                beli_barang(username, data)
                input("\nTekan Enter untuk kembali ke menu...")
            elif pilihan == "3":
                tampilkan_riwayat_pembelian(username, data)
                input("\nTekan Enter untuk kembali ke menu...")
            elif pilihan == "4":
                upgrade_ke_vip(username, data)
                input("\nTekan Enter untuk kembali ke menu...")
            elif pilihan == "5":
                top_up_saldo(username, data)
                input("\nTekan Enter untuk kembali ke menu...")
            elif pilihan == "0":
                print("Keluar dari menu utama...\n")
                time.sleep(5)
                return 
            else:
                print("Pilihan tidak valid! Coba lagi.")
                input("\nTekan Enter untuk kembali ke menu...")
        except Exception as e:
            print(f"Terjadi kesalahan: {e}")
            input("\nTekan Enter untuk kembali ke menu...")

def main():
    data = muat_database()
    while True:
        bersihkan_layar()
        print("=== Toko Game Rainbow Six Siege ===")
        print("1. Login")
        print("2. Daftar Member Baru")
        print("0. Keluar")
        pilihan = input("\nPilih menu: ").strip()

        if pilihan == "1":
            username = login(data)
            if username:
                menu_utama(username, data)  
        elif pilihan == "2":
            daftar_pengguna(data)
        elif pilihan == "0":
            print("Terima kasih telah menggunakan aplikasi ini!")
            time.sleep(5)
            break  
        else:
            print("Pilihan tidak valid.")
            input("\nTekan Enter untuk kembali ke menu...")

main()