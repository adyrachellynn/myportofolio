# Tugas 1: 
# Static Web with HTML5 and CSS3 - PBP Gasal 2026/2027

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
# Personal Portfolio Website - PBP

* **Nama**: Adyra Rachellyn Arkossand
* **NPM**: 2506620620
* **Kelas**: PBP C
* **Tautan Repositori**: [GitHub Repository](https://github.com/adyrachellynn/myportofolio)

---

### Tugas 2

#### Pertanyaan Reflektif

1. **Jelaskan alur yang terjadi ketika pengguna membuka halaman portofolio baru, mulai dari permintaan yang diterima proyek hingga data ditampilkan pada browser. Dalam jawabanmu, jelaskan peran urls.py proyek, urls.py aplikasi, view, model, dan template.**

   * **HTTP Request & `urls.py` Proyek**: Browser mengirim request ke rute `/education/`. Berkas routing root (`myportofolio/urls.py`) menangkap URL ini dan menggunakan `include('main.urls')` untuk delegasi rute ke aplikasi yang bersangkutan.
   * **`urls.py` Aplikasi**: Berkas `main/urls.py` mencocokkan path string `education/` dengan nama rute (`name='show_education'`) dan meneruskan eksekusi ke fungsi controller `show_education` di view.
   * **View (`views.py`)**: Fungsi view bertindak sebagai orchestrator logika bisnis. View memanggil ORM untuk mengambil data, menyusunnya ke dalam dictionary `context`, dan memanggil template renderer.
   * **Model (`models.py`)**: Model `Education` mengeksekusi query ORM (`Education.objects.all()`) ke database SQLite, mengembalikan sekumpulan instance record dalam bentuk QuerySet.
   * **Template (`templates/*.html`) & Response**: Django Template Engine (DTL) memproses file `education.html` dengan menyuntikkan data dari context (menggunakan looping dan filter status), lalu mengompilasinya menjadi respons HTTP statis (status 200 OK) untuk dirender di peramban.

2. **Mengapa data untuk bagian portofolio baru sebaiknya disimpan pada model dan tidak ditulis langsung di dalam template? Jelaskan dampaknya terhadap kemudahan pemeliharaan dan pengembangan aplikasi.**

   * **Separation of Concerns & Maintainability**: Memisahkan lapisan data dari lapisan presentasi. Menulis data langsung atau yang biasa disebut dengan hardcoded di template membuat markup HTML kotor (tidak clean) dan berisiko merusak struktur styling CSS/Bento Grid setiap kali ada riwayat baru yang ditambah atau diedit ^^
   * **Single Source of Truth & Reusability**: Data di dalam model tersimpan terpusat di database. Data ini dapat dengan mudah diekspos ke berbagai format lain di masa depan (misal: JSON API untuk mobile app) atau dimanipulasi via Django Admin tanpa perlu mengutak-atik berkas HTML.
   * **Integritas & Validasi Data**: Model menyediakan validasi skema otomatis (seperti pembatasan panjang karakter `max_length`, nilai default, dan tipe data).

3. **Apa perbedaan fungsi `makemigrations` dan `migrate` pada Django? Berikan contoh perubahan model yang mengharuskanmu menjalankan kedua perintah tersebut.**

   * **Perbedaan Fungsi**:
     * `python manage.py makemigrations`: Berfungsi membaca modifikasi skema pada `models.py` dan menghasilkan berkas cetak biru di direktori `migrations/`. Perintah ini umumnya belum mengubah struktur tabel fisik di database.
     * Sedangkan, `python manage.py migrate`: Berfungsi mengeksekusi berkas migrasi yang belum terpasang ke basis data fisik (membuat/memodifikasi tabel dan kolom di SQLite) serta mencatat statusnya di tabel riwayat `django_migrations`.
   * **Contoh Kasus**:
     Ketika menambahkan atribut atau field baru pada model `Education` (misal menambahkan field `degree`):
     ```python
     degree = models.CharField(max_length=100, default="")
     ```
     Perintah `makemigrations` wajib dijalankan agar Django menyusun berkas migrasi penambahan kolom `degree`, lalu dilanjutkan dengan `migrate` agar kolom tersebut terbuat di tabel database lokal.

---

#### Implementasi Checklist Tugas 2

1. **Menambahkan model baru pada aplikasi `main` (`Education`)**
   * *Yang dilakukan*: Bikin class model `Education` di `main/models.py`.
   * *Kenapa*: Pakai Django ORM biar data riwayat pendidikan punya struktur yang rapi, relasinya jelas, dan gampang dikembangin ke depannya.

2. **Model memiliki minimal 3 field selain primary key dengan tipe data sesuai**
   * *Yang dilakukan*: Ada field seperti institusi, jenjang/jurusan, tahun, dan deskripsi dengan tipe data semantik (`CharField`, `TextField`, dsb.).
   * *Kenapa*: Tipe datanya dipilih sesuai makna datanya, menjaga integritas database, dan memudahkan styling khusus pada kartu Bento Grid.

3. **Membuat dan menerapkan migrasi model serta menyertakan berkas migrasi dalam commit**
   * *Yang dilakukan*: Jalanin `python manage.py makemigrations` dan `migrate`, terus mastiin folder `main/migrations/` ke track di Git.

4. **Membuat view yang mengambil data model dan meneruskannya ke context template**
   * *Yang dilakukan*: Bikin fungsi `show_education` di `main/views.py` yang manggil `Education.objects.all()`, dibungkus jadi context `education_list`, terus di-render ke `templates/education.html`.
   * *Kenapa*: Viewnya bs tetap "tipis" (*thin view*) krn cuma ngambil data & nyiapin context, jadi arsitekturnya tetap modular ^^

5. **Menampilkan seluruh objek menggunakan perulangan DTL dan menyediakan fallback tampilan kosong**
   * *Yang dilakukan*: Pakai `{% for edu in education_list %}` dan `{% empty %}` di `templates/education.html`.
   * *Kenapa*: `{% empty %}` bikin tampilan tetap enak diliat pas datanya kosong, tanpa perlu nulis `if-else` bertingkat yang ribet di HTMLnya

6. **Data tidak ditulis langsung (hardcoded) di template HTML**
   * *Yang dilakukan*: Semua riwayat pendidikan diambil secara dinamis dari database via atribut objek model.
   * *Kenapa*: Nggak ada duplikasi markup, dan update portofolio bisa dilakuin kapan aja tanpa ubah kode tampilan

7. **Mendaftarkan named route pada `main/urls.py`**
   * *Yang dilakukan*: Nambahin `path('education/', show_education, name='show_education')` di `urlpatterns`.
   * *Kenapa*: Pakai `name='show_education'` misahin path URL dari referensi kode — kalau path-nya diubah nanti, nggak perlu ubah link satu-satu di semua template.

8. **Menambahkan tautan navbar menggunakan tag `{% url %}` dan menjaga konsistensi layout**
   * *Yang dilakukan*: Link menu pakai `{% url 'main:show_education' %}`, dan navbar (floating pill nav) + footer disamain di semua halaman (`index.html`, `education.html`, `experience.html`).
   * *Kenapa*: Reverse URL resolution bawaan Django ngurangin risiko broken link, dan navigasinya jadi konsisten di semua halaman.

9. **Menambahkan automated unit test (minimal 3 kasus pengujian)**
   * *Yang dilakukan*: Nulis test di `main/tests.py`, isinya:
     1. Cek status HTTP 200 dan template yang dipakai udah bener.
     2. Cek data riwayat kerender pas database ada isinya.
     3. Cek pesan *empty state* muncul pas data belum ada.
   * *Kenapa*: Biar bug/regresi ketauan lebih awal, dan alur MVT-nya udah kevalidasi otomatis sebelum kode di-push.

10. **Memastikan proyek bebas error dan seluruh unit test lolos**
    * *Yang dilakukan*: Jalanin `python manage.py test` (9 test lolos semua) dan `python manage.py runserver` jalan mulus tanpa error.
    * *Kenapa*: Biar yakin kodenya stabil dan reliable sebelum dikumpulin ke repo publik.

---

## Transparansi Penggunaan AI (AI Disclosure)

Dalam pengerjaan Tugas 2, saya menggunakan asisten AI (Gemini) sebagai rekan diskusi coding dan UI/UX partner! ><

### Tools yang Digunakan
* **Gemini** (Google DeepMind)

### Aspek yang Dibantu AI
* **Eksplor UI/UX**: AI membantu menyusun struktur CSS grid dan flexbox untuk mengubah tampilan kaku 4 kolom menjadi tata letak *Editorial Stacked List* pada halaman Experience, serta menyelaraskan hierarki visual Bento Grid di Education.
* **Penyelarasan Navbar**: Edit dan menyamakan item menu serta penamaan logo navbar di seluruh template (`index.html`, `experience.html`, `education.html`).
* **Pembersihan CSS**: Memeriksa dan menghapus aturan selektor yang tidak lagi terpakai di `static/css/style.css` setelah layout diganti.

### Strategi Prompting & Pengambilan Keputusan
* **Iteratif & Kritis**: Saya menyaring output yang disarankan AI, meminta alternatif jika hasil visual terlalu kaku, dan memastikan integrasi kode tetap sesuai arsitektur Django MVT.
* **Grounding Kode & Visual**: Melampirkan potongan template, skrip CSS, dan tangkapan layar langsung agar saran perbaikan presisi terhadap bug lokal.

### Cuplikan Log Interaksi
* *Prompt*: *"warna orange yg menyesuaikan dong. aku gasuka item begitu"*  
  *Aksi*: Menyesuaikan gradien kartu Bento Grid agar selaras dengan tema portofolio.
* *Prompt*: *"kenapa di pojok kiri jd nama lengkap aku ya halo"*  
  *Aksi*: Menyeragamkan identitas navbar menjadi `Adyra.` di seluruh template.
* *Prompt*: *"jujur gw agak kurang suka lagi hmchh. pgn dibikin beda gt gamau kotak2 doang"*  
  *Aksi*: Beralih dari kartu berpetak ke layout editorial timeline dua sisi (metadata status di kiri, rincian peran di kanan).
* *Prompt*: *"tp jujur td di css experience nya sia sia ya. diapus aja kan"*  
  *Aksi*: Membersihkan *dead code* di `style.css` agar berkas CSS tetap ringkas.