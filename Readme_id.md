# README untuk Advanced AVR Flasher GUI

## Gambaran Umum
**Advanced AVR Flasher GUI** adalah aplikasi berbasis PyQt6 yang dirancang untuk mempermudah pemrograman, pengelolaan, dan troubleshooting mikrokontroler AVR. Aplikasi ini menyediakan antarmuka pengguna yang ramah untuk memilih chip, mem-flash firmware, membaca/menulis EEPROM, memodifikasi bit fuse, dan melakukan verifikasi serta debugging. Program ini menggunakan alat baris perintah `avrdude` untuk berinteraksi langsung dengan perangkat AVR.

## Fitur
1. **Basis Data Chip**: Mendukung berbagai jenis mikrokontroler AVR (ATmega, ATtiny, ATxmega, AVR32, AT90).
2. **Operasi Flash**:
   - Memilih dan menulis firmware dalam format `.hex`.
   - Membaca dan memverifikasi memori flash.
3. **Operasi EEPROM**:
   - Membaca, menulis, dan memverifikasi data EEPROM.
4. **Manajemen Fuse**:
   - Melihat dan memodifikasi pengaturan fuse.
   - Mengembalikan nilai fuse ke default.
5. **Pengaturan Lanjutan**:
   - Mengonfigurasi periode bit clock dan jumlah percobaan ulang.
   - Mengaktifkan/mematikan opsi seperti penghapusan sebelum menulis atau verifikasi fuse.
6. **Output Konsol**:
   - Menampilkan keluaran dan progres perintah `avrdude` secara real-time.
7. **Penyimpanan Preferensi**:
   - Menyimpan dan memulihkan preferensi pengguna seperti keluarga chip, pengaturan lanjutan, dan lainnya.

## Persyaratan
### Perangkat Lunak
- Python 3.8+
- Library Python yang Dibutuhkan:
  - `PyQt6`
  - `json`
  - `subprocess`
- `avrdude` (Harus diinstal dan dikonfigurasi dalam PATH sistem)

### Perangkat Keras
- Mikrokontroler AVR yang didukung dengan programmer yang sesuai (misalnya, USBasp, STK500).

## Instalasi
1. Clone atau unduh repositori yang berisi file ini.
2. Pastikan Python 3.8+ telah terpasang di sistem Anda.
3. Instal library Python yang diperlukan:
   ```bash
   pip install PyQt6
   ```
4. Pastikan `avrdude` telah diinstal:
   - Untuk Linux:
     ```bash
     sudo apt install avrdude
     ```
   - Untuk Windows:
     Unduh dan instal versi terbaru dari `avrdude`, lalu tambahkan ke PATH sistem.
5. Jalankan aplikasi:
   ```bash
   python advance.py
   ```

## Petunjuk Penggunaan
1. **Menjalankan Aplikasi**:
   - Jalankan `python advance.py` dari command line.
   - Jendela utama akan muncul, menampilkan beberapa tab untuk memilih chip, operasi flash, EEPROM, manajemen fuse, dan pengaturan lanjutan.

2. **Pemilihan Chip**:
   - Pilih keluarga chip dari menu drop-down.
   - Pilih model chip spesifik.

3. **Operasi Flash**:
   - Gunakan tombol **"Pilih File Hex"** untuk memuat firmware Anda.
   - Tulis ke memori flash menggunakan tombol **"Tulis Flash"**.
   - Baca atau verifikasi memori flash yang ada menggunakan tombol **"Baca Flash"** atau **"Verifikasi Flash"**.

4. **Operasi EEPROM**:
   - Gunakan tombol **"Pilih File EEPROM"** untuk memilih file EEPROM.
   - Tulis data ke EEPROM dengan tombol **"Tulis EEPROM"**.
   - Baca atau verifikasi data EEPROM menggunakan tombol terkait.

5. **Manajemen Fuse**:
   - Lihat pengaturan fuse default atau yang ada.
   - Modifikasi nilai dan tulis menggunakan tombol **"Tulis Fuse"**.
   - Kembalikan nilai fuse ke pengaturan default dengan tombol **"Atur Ulang ke Default"**.

6. **Output Konsol**:
   - Pantau progres dan pesan kesalahan secara real-time melalui jendela konsol di bagian bawah aplikasi.
   - Gunakan tombol **"Bersihkan Konsol"** untuk menghapus output.

7. **Pengaturan Lanjutan**:
   - Konfigurasikan periode bit clock dan jumlah percobaan ulang.
   - Aktifkan atau nonaktifkan opsi seperti penghapusan sebelum menulis atau verifikasi fuse.

## Catatan Pengembang
- `CHIP_DATABASE` menyediakan spesifikasi lengkap untuk berbagai chip AVR, termasuk ukuran memori, nilai fuse default, dan deskripsi. Basis data ini dapat diperluas sesuai kebutuhan.
- `AvrdudeWorker` diimplementasikan menggunakan `QThread` PyQt untuk menjalankan perintah secara asinkron, memastikan GUI tetap responsif.
- Pengaturan dikelola menggunakan `QSettings`, memungkinkan preferensi pengguna bertahan di antara sesi.

## Pemecahan Masalah
- **Ketergantungan Hilang**:
  - Pastikan semua library Python yang diperlukan telah diinstal.
  - Verifikasi bahwa `avrdude` terpasang dengan benar dan dapat diakses melalui command line.
- **Kesalahan Izin**:
  - Di Linux, pastikan pengguna memiliki izin untuk mengakses perangkat programmer (misalnya, USBasp).
- **Chip Tidak Terdeteksi**:
  - Periksa koneksi, pengaturan programmer, dan pemilihan chip.
  - Cek dokumentasi chip untuk pengaturan fuse dan clock yang benar.

## Penghargaan
Proyek ini dirancang untuk menyederhanakan pemrograman dan pengelolaan mikrokontroler AVR, membuatnya lebih mudah diakses oleh hobiis maupun profesional. Aplikasi ini memanfaatkan alat `avrdude` yang andal untuk fungsi utamanya.

## Rencana Pengembangan
- Integrasi dengan programmer dan antarmuka tambahan.
- Dukungan untuk protokol debugging lanjutan.
- Penanganan kesalahan dan diagnostik yang lebih baik.

Nikmati kemudahan memrogram mikrokontroler AVR Anda! 🚀
