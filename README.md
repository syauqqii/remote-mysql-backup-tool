# Remote MySQL Backup Tool

`remote-mysql-backup-tool` adalah skrip Python yang digunakan untuk melakukan backup otomatis database MySQL pada server jarak jauh (remote) melalui SSH. Skrip ini memungkinkan untuk membuat, mentransfer, dan memulihkan backup database MySQL dari server jarak jauh ke server lokal, serta menghapus backup lama berdasarkan jumlah hari yang ditentukan.

## Fitur

- Backup database MySQL jarak jauh secara otomatis.
- Transfer backup dari server jarak jauh ke server lokal menggunakan SCP.
- Pulihkan backup secara otomatis ke server MySQL lokal.
- Hapus backup lama berdasarkan jumlah hari yang ditentukan.
- Konfigurasi fleksibel menggunakan file `config.json`.

## Prasyarat

Pastikan Anda memiliki hal-hal berikut sebelum menjalankan skrip ini:

- Python `3.x`
- Library Python: `paramiko`, `scp`, `mysqlclient`
- Akses SSH ke server jarak jauh
- Akses MySQL di server jarak jauh dan lokal

## Instalasi

1. **Clone Repository:**

   ```bash
   git clone https://github.com/syauqqii/remote-mysql-backup-tool
   cd remote-mysql-backup-tool
   ```

2. **Instal Dependensi:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Konfigurasi:**

   Penjelasan Konfigurasi:

   - deletedays: Jumlah hari sebelum backup dihapus secara otomatis.
   - localuser: User MySQL lokal untuk mengimpor backup.
   - localpass: Password user MySQL lokal.
   - backups: Daftar server dan database yang akan di-backup.

2. **Jalankan Script:**

   Untuk menjalankan skrip dan melakukan backup:

   ```bash
   python main.py
   ```

   Untuk menjalankan skrip tanpa mengimpor backup ke server lokal:

   ```bash
   python main.py --norestore
   ```

## Log

Log proses backup dan kesalahan akan dicatat dalam file logs/backup.log

## Todo

- [ ]  Tambahkan opsi untuk menonaktifkan fitur penghapusan otomatis.
- [ ]  Izinkan login ke SSH menggunakan password (saat ini menggunakan SSH key).

## Kontribusi

Kontribusi selalu diterima! Silakan lakukan fork pada repository ini dan ajukan pull request jika Anda memiliki peningkatan atau fitur baru.
