## 🛠️ Instalasi & Konfigurasi Environment

Proyek ini memerlukan instalasi library Python serta software eksternal untuk mendukung fitur OCR.

### 1. Instalasi Dependensi Python

Pastikan Python 3.8+ sudah terinstall. Lalu jalankan:

```bash
pip install -r requirements.txt

```

### 2. Instalasi Software Eksternal (Wajib untuk OCR)

Karena modul main3.py menangani PDF gambar, Anda WAJIB menginstall dua software berikut di sistem operasi Windows Anda. Tanpa ini, program akan error saat memproses file scan.

#### A. Tesseract-OCR (Mesin Pengenal Teks)

Digunakan oleh library pytesseract untuk mengenali karakter dari gambar.

1. Download Installer: [UB-Mannheim Tesseract GitHub](https://github.com/UB-Mannheim/tesseract/wiki?spm=a2ty_o01.29997173.0.0.49f755fb8UqXhb)
2. Proses Instalasi:
   - Jalankan file .exe yang diunduh.
   - Saat muncul pilihan komponen (Choose Components), PENTING: Centang opsi "Additional language data" -> lalu pilih Indonesian (ind) dan English (eng). Ini agar OCR bisa membaca bahasa Indonesia dengan baik.
   - Selesaikan instalasi.
   - Catat path instalasi (default biasanya: C:\Program Files\Tesseract-OCR).
3. Verifikasi:
   - Buka CMD atau PowerShell.
   - Ketik: tesseract --version
   - Jika muncul nomor versi, instalasi berhasil.

#### B. Poppler (PDF Rendering Engine)

Digunakan oleh library pdf2image untuk mengubah halaman PDF menjadi gambar (PNG/JPG) sebelum di-proses oleh Tesseract.

1. Download Binary: Unduh release terbaru untuk Windows dari [Poppler for Windows by oschwartz10612](https://github.com/oschwartz10612/poppler-windows/releases/?spm=a2ty_o01.29997173.0.0.49f755fb8UqXhb). Pilih file zip terbaru (misal: Release-xx.xx.x-0.zip).
2. Ekstrak & Pindahkan:
   - Extract file zip tersebut.
   - Pindahkan folder hasil extract (misalnya bernama poppler-xx.xx.x) ke lokasi permanen yang mudah diakses.
   - Rekomendasi: Pindahkan ke C:\Tools\poppler atau D:\Tools\poppler.

##### Untuk menjalankan di windows mohon ganti kode di ekstraksi_pdf.py dan sesuaikan dengan ruang lingkup anda

```bash
# sesuaikan path dengan path anda
POPPLER_PATH = r'E:\data\poppler-25.12.0\Library\bin'
pytesseract.pytesseract.tesseract_cmd = r'E:\data\tesseract\tesseract.exe'

```

### Untuk Build ke docker harap ganti url mongodbnya di .env

### di file ekstraksi_pdf.py komentari baris berikut

```bash
# komentari baris ini dan hapus variabel POPPLER_PATH disetiap pemanggilan
POPPLER_PATH = r'E:\data\poppler-25.12.0\Library\bin'
pytesseract.pytesseract.tesseract_cmd = r'E:\data\tesseract\tesseract.exe'

```

#### Untuk menggnakan API protected pada header set bagian Authorization

```bash
# ganti token setelah barier tersebut dengan token yang didapat dari setelah login
Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNmEyODBlNTY4YWI5OWI2YWNkOWRiNGYyIiwiZXhwIjoxNzgxMDk2NDE0fQ.pzrCDebOvqL_vmwxcx5ELVluSEVOGVMoJfZeprf5kkU
```

3. Instalasi MongoDB Compass
   - Download MongoDB Compass
     Kunjungi situs resmi: https://www.mongodb.com/try/download/compass
     Pilih versi yang sesuai dengan sistem operasi Anda (Windows, macOS, atau Linux)
     Download installer-nya
   - Instalasi di Windows
     Jalankan file .exe yang sudah didownload
     Ikuti wizard instalasi (Next → Next → Install)
     Tunggu proses instalasi selesai
     Klik "Finish" untuk menyelesaikan

4. Menggunakan MongoDB Compass
   - Koneksi ke Database
     Buka MongoDB Compass
     Masukkan connection string:
     Lokal: mongodb://localhost:27017
     Atlas: Copy dari MongoDB Atlas dashboard
     Klik "Connect"
   - Membuat Database Baru
     Setelah terhubung, klik "Create Database"
     Masukkan nama database
     Masukkan nama collection pertama
     Klik "Create Database"
   - Menambahkan Data
     Pilih collection yang ingin ditambahkan data
     Klik "Add Data" → "Insert Document"
     Masukkan data dalam format JSON
     Klik "Insert"
   - Query Data
     Gunakan tab "Filter" untuk mencari data
     Contoh filter: { "nama": "John" }
     Klik "Find" untuk melihat hasil

### Download model

- Download model [best.pt](https://drive.google.com/file/d/1uVaXEthrhJNDm0rqZc2qNO1tMuohsxTG/view?usp=drive_link) pastikan menggunakan email devacademi yang diizinkan
- taruh model best.pt di root file

## 🔗 API Integration

### Base URL

- **Development**: `http://127.0.0.1:5000`
- **Production**: Set `REACT_APP_API_URL` in `.env`

### Authentication Endpoints

#### Register User

```
POST /api/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePassword123"
}

Response: 201 Created
{
  "message": "User registered successfully!"
}
```

#### Login User

```
POST /api/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "SecurePassword123"
}

Response: 200 OK
{
  "message": "Login successful!",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "username": "john_doe",
    "email": "john@example.com"
  }
}
```

#### Analyze

```
POST /api/analyze
Content-Type: application/json

{
  "job_description": "ISIKAN JD NYA",
  "image": "[file1], [file2]"
}

Response: 200 OK
{
    "data": {
        "job_deskription": "Senior Full Stack Engineer (.NET/PHP/Node Focus)\n\n    We are looking for an experienced Full Stack Developer to join our agile team building scalable web applications for the hospitality and gaming industries.\n\n    Responsibilities:\n    - Develop and maintain backend services using Symfony, Node.js, or .NET frameworks.\n    - Build responsive front-end interfaces using React.js, Vue.js, or TypeScript.\n    - Collaborate with product managers and designers in a Scrum/Agile environment.\n    - Implement automated testing (Jest, PHPUnit, Selenium) to ensure code quality.\n    - Optimize database performance (MySQL, Redis) and handle API integrations.\n\n    Requirements:\n    - 5+ years of experience in full stack development.\n    - Strong proficiency in JavaScript/TypeScript and modern frontend frameworks (React/Vue).\n    - Experience with backend technologies such as PHP (Symfony), Node.js, or C#.\n    - Familiarity with cloud services (AWS, Firebase) and CI/CD pipelines.\n    - Experience in porting applications or working with gaming/hospitality platforms is a plus.\n    - Strong understanding of RESTful APIs and microservices architecture.",
        "result": [
            {
                "cv_struct": "[RESUME]\n\nSUMMARY:\nlanguages python sql java frameworks pandas numpy scikit learn matplothb tools power bl excel powerpoint tableau mysql sqlite platforms pycharm jupyter notebook visual studio code intellij idea soft projects\n\nSKILLS:\nrapport building strong stakeholder management people management excelent communication\n\nEDUCATION:\nvellore institute technology bhopal india master computer application gpa june august barasat govt college kolkata india bachelor science honors mathematics gpa june august",
                "name": "ae19a6d09e6228cc7309a93301c59fd7",
                "score": 0.030681271106004715
            },
            {
                "cv_struct": "[RESUME]\n\nSUMMARY:\nseasoned full stack developer widely recognized creating robust web apps achieved impressive boost user interaction andby skillfully introducing unique functionalities techsolutions techy street san francisco comrep johnathanreed\n\nSKILLS:\nlead full stack developer techsolutions ca spearheaded team developing scalable modern web application ledtoa increase user engagement improved customer satisfaction implemented continuous integration deployment pipelines resulting ina reduction deployment time enhancing overall system efficiency enhanced site security efficiency advanced coding practices utilization modern frameworks conducting regular system audits front end development html css javascript reactjs back end development nodejs express js mongodb restful apis python senior full stack developer eee codecrafters ny devops testing aws docker jenkins nagios designed executed\n\nEXPERIENCE:\nprofessional\n\nEDUCATION:\npersonal",
                "name": "7b0fcd20e8a8c9d464b9d42869971538",
                "score": 0.011417971923947334
            }
        ]
    },
    "message": "Success",
    "status": 200
}

```

#### Screenings

```
GEt /api/screenings
Content-Type: application/json

Response: 200 OK
{
    "data": [
        {
            "created_at": "Mon, 15 Jun 2026 18:56:08 GMT",
            "job_deskription": "Senior Full Stack Engineer (.NET/PHP/Node Focus)\n\n    We are looking for an experienced Full Stack Developer to join our agile team building scalable web applications for the hospitality and gaming industries.\n\n    Responsibilities:\n    - Develop and maintain backend services using Symfony, Node.js, or .NET frameworks.\n    - Build responsive front-end interfaces using React.js, Vue.js, or TypeScript.\n    - Collaborate with product managers and designers in a Scrum/Agile environment.\n    - Implement automated testing (Jest, PHPUnit, Selenium) to ensure code quality.\n    - Optimize database performance (MySQL, Redis) and handle API integrations.\n\n    Requirements:\n    - 5+ years of experience in full stack development.\n    - Strong proficiency in JavaScript/TypeScript and modern frontend frameworks (React/Vue).\n    - Experience with backend technologies such as PHP (Symfony), Node.js, or C#.\n    - Familiarity with cloud services (AWS, Firebase) and CI/CD pipelines.\n    - Experience in porting applications or working with gaming/hospitality platforms is a plus.\n    - Strong understanding of RESTful APIs and microservices architecture.",
            "result": [
                {
                    "cv_struct": "[RESUME]\n\nSUMMARY:\nlanguages python sql java frameworks pandas numpy scikit learn matplothb tools power bl excel powerpoint tableau mysql sqlite platforms pycharm jupyter notebook visual studio code intellij idea soft projects\n\nSKILLS:\nrapport building strong stakeholder management people management excelent communication\n\nEDUCATION:\nvellore institute technology bhopal india master computer application gpa june august barasat govt college kolkata india bachelor science honors mathematics gpa june august",
                    "name": "ae19a6d09e6228cc7309a93301c59fd7",
                    "score": 0.030681271106004715
                },
                {
                    "cv_struct": "[RESUME]\n\nSUMMARY:\nseasoned full stack developer widely recognized creating robust web apps achieved impressive boost user interaction andby skillfully introducing unique functionalities techsolutions techy street san francisco comrep johnathanreed\n\nSKILLS:\nlead full stack developer techsolutions ca spearheaded team developing scalable modern web application ledtoa increase user engagement improved customer satisfaction implemented continuous integration deployment pipelines resulting ina reduction deployment time enhancing overall system efficiency enhanced site security efficiency advanced coding practices utilization modern frameworks conducting regular system audits front end development html css javascript reactjs back end development nodejs express js mongodb restful apis python senior full stack developer eee codecrafters ny devops testing aws docker jenkins nagios designed executed\n\nEXPERIENCE:\nprofessional\n\nEDUCATION:\npersonal",
                    "name": "7b0fcd20e8a8c9d464b9d42869971538",
                    "score": 0.011417971923947334
                }
            ]
        },
        {
            "created_at": "Mon, 15 Jun 2026 18:03:45 GMT",
            "job_deskription": "Senior Full Stack Engineer (.NET/PHP/Node Focus)\n\n    We are looking for an experienced Full Stack Developer to join our agile team building scalable web applications for the hospitality and gaming industries.\n\n    Responsibilities:\n    - Develop and maintain backend services using Symfony, Node.js, or .NET frameworks.\n    - Build responsive front-end interfaces using React.js, Vue.js, or TypeScript.\n    - Collaborate with product managers and designers in a Scrum/Agile environment.\n    - Implement automated testing (Jest, PHPUnit, Selenium) to ensure code quality.\n    - Optimize database performance (MySQL, Redis) and handle API integrations.\n\n    Requirements:\n    - 5+ years of experience in full stack development.\n    - Strong proficiency in JavaScript/TypeScript and modern frontend frameworks (React/Vue).\n    - Experience with backend technologies such as PHP (Symfony), Node.js, or C#.\n    - Familiarity with cloud services (AWS, Firebase) and CI/CD pipelines.\n    - Experience in porting applications or working with gaming/hospitality platforms is a plus.\n    - Strong understanding of RESTful APIs and microservices architecture.",
            "result": [
                {
                    "cv_struct": "[RESUME]\n\nSUMMARY:\nlanguages python sql java frameworks pandas numpy scikit learn matplothb tools power bl excel powerpoint tableau mysql sqlite platforms pycharm jupyter notebook visual studio code intellij idea soft projects\n\nSKILLS:\nrapport building strong stakeholder management people management excelent communication\n\nEDUCATION:\nvellore institute technology bhopal india master computer application gpa june august barasat govt college kolkata india bachelor science honors mathematics gpa june august",
                    "name": "ae19a6d09e6228cc7309a93301c59fd7",
                    "score": 0.030681271106004715
                },
                {
                    "cv_struct": "[RESUME]\n\nSUMMARY:\nseasoned full stack developer widely recognized creating robust web apps achieved impressive boost user interaction andby skillfully introducing unique functionalities techsolutions techy street san francisco comrep johnathanreed\n\nSKILLS:\nlead full stack developer techsolutions ca spearheaded team developing scalable modern web application ledtoa increase user engagement improved customer satisfaction implemented continuous integration deployment pipelines resulting ina reduction deployment time enhancing overall system efficiency enhanced site security efficiency advanced coding practices utilization modern frameworks conducting regular system audits front end development html css javascript reactjs back end development nodejs express js mongodb restful apis python senior full stack developer eee codecrafters ny devops testing aws docker jenkins nagios designed executed\n\nEXPERIENCE:\nprofessional\n\nEDUCATION:\npersonal",
                    "name": "7b0fcd20e8a8c9d464b9d42869971538",
                    "score": 0.011417971923947334
                }
            ]
        }
    ],
    "message": "Success",
    "status": 200
}

```

#### Ranking

```
GEt /api/ranking/<screning_id>
Content-Type: application/json

Response: 200 OK
{
    "data": {
        "created_at": "Mon, 15 Jun 2026 18:03:45 GMT",
        "job_description_preview": "Senior Full Stack Engineer (.NET/PHP/Node Focus)\n\n    We are looking for an experienced Full Stack D...",
        "ranked_list": [
            {
                "cv_struct": "[RESUME]\n\nSUMMARY:\nlanguages python sql java frameworks pandas numpy scikit learn matplothb tools power bl excel powerpoint tableau mysql sqlite platforms pycharm jupyter notebook visual studio code intellij idea soft projects\n\nSKILLS:\nrapport building strong stakeholder management people management excelent communication\n\nEDUCATION:\nvellore institute technology bhopal india master computer application gpa june august barasat govt college kolkata india bachelor science honors mathematics gpa june august",
                "name": "ae19a6d09e6228cc7309a93301c59fd7",
                "rank": 1,
                "score": 0.0307
            },
            {
                "cv_struct": "[RESUME]\n\nSUMMARY:\nseasoned full stack developer widely recognized creating robust web apps achieved impressive boost user interaction andby skillfully introducing unique functionalities techsolutions techy street san francisco comrep johnathanreed\n\nSKILLS:\nlead full stack developer techsolutions ca spearheaded team developing scalable modern web application ledtoa increase user engagement improved customer satisfaction implemented continuous integration deployment pipelines resulting ina reduction deployment time enhancing overall system efficiency enhanced site security efficiency advanced coding practices utilization modern frameworks conducting regular system audits front end development html css javascript reactjs back end development nodejs express js mongodb restful apis python senior full stack developer eee codecrafters ny devops testing aws docker jenkins nagios designed executed\n\nEXPERIENCE:\nprofessional\n\nEDUCATION:\npersonal",
                "name": "7b0fcd20e8a8c9d464b9d42869971538",
                "rank": 2,
                "score": 0.0114
            }
        ],
        "screening_id": "6a303e81618759571b8c1361",
        "total_candidates": 2
    },
    "message": "Success",
    "status": 200
}


```
