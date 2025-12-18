

# Cloud File Converter (DOCX ↔ PDF)

A cloud-based web application that converts files between **DOCX** and **PDF** formats using **Python Flask** and **AWS EC2**.

This project was developed for **CpE-402: Cloud Computing** at **Kuwait University**.

---

## Tech Stack

* **Backend:** Python (Flask)
* **Cloud Platform:** AWS

  * EC2
  * S3
* **Frontend:** HTML, CSS
* **File Processing:** Server-side conversion libraries

---

## How It Works

1. User uploads a DOCX or PDF file through the web interface.
2. The Flask backend running on EC2 processes the file.
3. The file is converted to the requested format.
4. The converted file is provided for download.

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

1. Launch an AWS EC2 instance.
2. Open inbound port **5000** in the security group.
3. Install dependencies on the instance.
4. Run the application:

```bash
python3 app.py
```

5. Access the app using:

```
http://EC2-PUBLIC-IP:5000
```

---

## AWS Configuration

* **EC2:** Hosts the Flask backend application
* **S3:** Stores uploaded and converted files

---

## Limitations

* Complex document layouts may not convert perfectly
* Scanned PDFs require OCR (not implemented)
* Designed for academic demonstration purposes


