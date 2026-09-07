# Tugas 1: Static Web with HTML5 and CSS3 - PBP Gasal 2026/2027

- **Nama**: Adyra Rachellyn
- **NPM**: 2506620620
- **Kelas**: PBP C
- **Tautan PWS**: http://adyra-rachellyn-myportofolio.pws.cs.ui.ac.id
- **Tautan Repositori GitHub**: https://github.com/adyrachellynn/myportofolio

---

## Deskripsi Aplikasi & Fitur

Portofolio web berbasis Django yang mengusung desain minimalis dengan konsep bento grid. Beberapa fitur yang tersedia:

- **About / Profil Diri**: Menampilkan data diri, latar belakang pendidikan, sertifikasi, serta ringkasan pengalaman dan pendekatan kerja penulis di bagian awal halaman.
- **Interactive Project Showcase**: Menampilkan proyek-proyek unggulan (LYPS Ed-Tech, 255 Digital Media Platform, dan PeduliKeluarga) yang dapat diklik untuk melihat studi kasus lengkap dari masing masing proyek.
- **Life & Snapshots**: Galeri personal of myself yang menampilkan sisi kehidupan di luar dunia coding dan kampus. Dari pendakian gunung hingga momen sehari hari, sebagai bentuk keseimbangan antara "baris kode" dan kehidupan nyata #LifeWorkBalance ^^
- **Responsive Layout**: Tampilan responsif menggunakan Tailwind/CSS custom agar navigasi tetap nyaman diakses dari berbagai ukuran perangkat.

---

## Cara Menjalankan Aplikasi (Setup)

1. Clone repositori ini:
   ```bash
   git clone https://github.com/adyrachellynn/myportofolio.git
   cd myportofolio
   ```
2. Buat dan aktifkan virtual environment:
   ```bash
   python -m venv env
   source env/bin/activate      # Mac/Linux
   env\Scripts\activate         # Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Jalankan migrasi database:
   ```bash
   python manage.py migrate
   ```
5. Jalankan server lokal:
   ```bash
   python manage.py runserver
   ```
6. Buka `http://localhost:8000` di browser.

---

## Pertanyaan Reflektif

### 1. Penggunaan Elemen Semantik HTML5

Ya, saya menggunakan elemen semantik HTML5 seperti `<header>`, `<main>`, `<section>`, `<article>`, `<figure>`, dan `<footer>`. Elemen-elemen ini membantu membagi struktur halaman secara lebih jelas dan bermakna, dibanding hanya menumpuk `<div>` tanpa konteks. Selain memudahkan pembacaan dan pemeliharaan kode, penggunaan elemen semantik juga mempermudah penerapan layout CSS Grid/Flexbox per kontainer, serta mendukung aksesibilitas (screen reader) dan SEO.

### 2. Tantangan Responsivitas CSS & Evaluasi Tampilan Mobile

Tantangan yang paling terasa adalah menyesuaikan bento grid multi-kolom dan galeri horizontal agar tidak terpotong atau terlalu padat saat ditampilkan di layar kecil. Beberapa penyesuaian yang saya lakukan:

- **Penataan ulang layout**: Pada desktop, bagian profil dan ringkasan ditampilkan berdampingan. Sementara di layar mobile, layout diubah menjadi satu kolom (`flex-direction: column` atau `grid-template-columns: 1fr`) agar pengguna cukup melakukan scroll vertikal.
- **Penyesuaian ukuran elemen**: Ukuran tipografi judul dan padding diperkecil, sedangkan kartu galeri dibuat menggunakan *horizontal scroll snap* dengan touch affordance agar tetap nyaman digeser dengan jari tanpa membuat halaman overflow ke samping.

### 3. Batasan Static Web & Rencana Fungsionalitas Dinamis

Batasan utama dari static web adalah konten yang sifatnya hardcoded langsung di dalam berkas HTML. Setiap kali ingin menambah proyek baru, memperbarui data portofolio, atau mengubah deskripsi, saya perlu mengedit source code secara manual.

Untuk iterasi selanjutnya dengan arsitektur MVT Django, beberapa fungsionalitas dinamis yang ingin saya persiapkan:

- Integrasi model database untuk menyimpan data proyek, tautan, dan galeri secara terstruktur.
- Halaman admin/form untuk menambah atau memperbarui konten portofolio tanpa perlu menyentuh kode HTML.
- Pengambilan dan rendering data secara dinamis dari database melalui views Django.

---

## AI Disclosure

Dalam pengerjaan tugas ini, saya menggunakan **Gemini** sebagai alat bantu (AI assistant), khususnya untuk:

- **Struktur HTML/layout**: Meminta saran susunan elemen semantik dan pembagian section (bento grid) yang sesuai dengan konten portofolio.
- **Styling CSS/responsif**: Berdiskusi soal pendekatan responsive design, termasuk cara menangani bento grid multi-kolom dan horizontal scroll snap agar tidak overflow di layar kecil.
- **Debugging/troubleshooting**: Membantu menemukan penyebab bug pada layout dan interaksi (misalnya elemen yang tidak sejajar atau scroll yang tidak smooth).

Semua saran dari AI tetap saya tinjau dan sesuaikan secara manual dengan konten dan gaya desain portofolio saya sendiri, terutama pada bagian data diri, deskripsi proyek, dan narasi Life & Snapshots yang bersifat personal.