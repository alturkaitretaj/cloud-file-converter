
# Cloud File Converter (DOCX ↔ PDF)

A simple cloud-based web application that converts files between DOCX and PDF formats using Python Flask and AWS services.


---

## Tech Stack

* **Backend:** Python (Flask)
* **Cloud Platform:** AWS

  * EC2
  * S3
  * IAM
* **Frontend:** HTML, CSS
* **File Processing:** Server-side conversion libraries

---

## How It Works

1. User uploads a DOCX or PDF file.
2. The Flask backend processes the file.
3. The file is converted to the requested format.
4. The converted file is available for download.

---

## Architecture

```
User → Browser → Flask App (EC2) → File Conversion → S3 → Download
```

---

## Repository Structure

```
cloud-file-converter/
├── app.py
├── templates/
│   └── index.html
├── static/
│   └── style.css
├── uploads/
├── outputs/
└── README.md
```

---

## Running the Project

1. Launch an EC2 instance.
2. Open port **5000** in the security group.
3. Install dependencies.
4. Run:

```bash
python3 app.py
```

5. Access the app at:

```
http://EC2-PUBLIC-IP:5000
```

---

## AWS Configuration

* **EC2:** Hosts the Flask application
* **S3:** Stores uploaded and converted files
* **IAM:** Manages permissions securely without hardcoded credentials

---

## Limitations

* Complex PDFs may not fully preserve layout
* OCR for scanned PDFs is not supported
* Intended for academic demonstration purposes

