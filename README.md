# Cloud-Based File Conversion System (DOCX ↔ PDF)

## Overview
This project implements a cloud-based document conversion system that allows users to convert files between **Word (DOCX)** and **PDF** formats. The system is built using a **Python Flask backend** deployed on **AWS infrastructure** and integrates cloud services to demonstrate server-side processing, object storage, event-driven computing, and secure access control.

Users interact with the system through a simple web interface where they upload a document, choose the conversion type, and download the converted file.

---

## System Architecture
The system follows a cloud-based client–server architecture:

1. A web-based frontend allows users to upload documents and select the conversion type.
2. A Flask backend running on an AWS EC2 instance handles file processing.
3. Document conversion is performed using server-side libraries.
4. Amazon S3 is used for cloud storage and automated workflows.
5. AWS Lambda supports event-driven file processing when files are uploaded to S3.
6. IAM roles manage secure access between AWS services.

---

## AWS Services Used
- **Amazon EC2**: Hosts the Flask backend and handles document conversion.
- **Amazon S3**: Stores input and output files and triggers automated workflows.
- **AWS Lambda**: Performs event-driven file conversion triggered by S3 uploads.
- **AWS IAM**: Manages permissions securely without hardcoding credentials.

---

## Backend Implementation
The backend is implemented using **Python Flask** and provides the following routes:

- `/`  
  Serves the web interface.

- `/health`  
  Health-check endpoint to verify server availability.

- `/docx2pdf`  
  Converts DOCX files to PDF using **Pandoc** and **LibreOffice**.

- `/pdf2docx`  
  Converts PDF files to DOCX using the **pdf2docx** library and **PyMuPDF**.

Converted files are returned directly to the user through the browser or stored in S3 for automated workflows.

---

## Frontend Interface
The frontend is a lightweight HTML page integrated with Flask. It provides:
- File upload functionality
- Conversion type selection
- Automatic file download after successful conversion

JavaScript is used to send files to the backend and handle responses without reloading the page.

---

## Setup Instructions

### 1. EC2 Environment Setup
- Launch an Ubuntu EC2 instance
- Open port **5000** in the EC2 security group
- Install required system dependencies:

```bash
sudo apt update
sudo apt install pandoc libreoffice python3-venv -y

### 2. Application Setup
```bash
git clone <your-repository-url>
cd scripts
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt


### 3. Run the Application
```bash
python3 docxconverter_app.py

### 4. Sample Output
The screenshots/ directory contains sample outputs of the running application, including:
Web interface home page
DOCX → PDF conversion result
PDF → DOCX conversion result

### 5. Security Configuration
IAM roles are used instead of AWS access keys.
S3 buckets are configured as private with no public access.
EC2 security group allows inbound traffic only on port 5000.
SSH access is restricted to the developer’s IP.
Presigned URLs are used for secure temporary file access.

### 5. Limitations
PDF to DOCX conversion may not fully preserve complex layouts.
Scanned PDFs require OCR, which is not implemented.
The system is intended for academic demonstration purposes.

### 6. AWS Deployment and Security Notes
EC2 security groups restrict inbound traffic to port 5000 only.
IAM roles are used instead of embedding AWS credentials in code.
Access to S3 buckets is limited to required permissions.
The EC2 instance is stopped when not in use to prevent unnecessary costs.

