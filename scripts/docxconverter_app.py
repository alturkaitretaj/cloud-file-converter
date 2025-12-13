
import os
import uuid
import subprocess
from pdf2docx import Converter

import boto3
import pypandoc
from flask import Flask, request, jsonify, render_template_string, send_file

app = Flask(__name__)

# ---------- Config ----------
UPLOADS_BUCKET = "doc-input-conversion"
OUTPUT_BUCKET  = "doc-output-conversion"

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR  = os.path.join(BASE_DIR, "inputs")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

HOME_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Cloud File Converter</title>
  <style>
    :root{
      --bg1:#eef3ff;
      --bg2:#f7f1ff;
      --card:#ffffff;
      --text:#1b2b41;
      --muted:#6b7a90;
      --primary:#2a6592;
      --primary2:#1d4767;
      --danger:#d12f2f;
      --ok:#1b8a3a;
      --shadow: 0 18px 45px rgba(17, 35, 64, .12);
      --radius: 16px;
    }
    *{box-sizing:border-box}
    body{
      margin:0;
      font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
      min-height:100vh;
      display:flex;
      align-items:center;
      justify-content:center;
      background: radial-gradient(1200px 600px at 30% 10%, var(--bg1), transparent),
                  radial-gradient(900px 500px at 80% 20%, var(--bg2), transparent),
                  #f7f9fb;
      color:var(--text);

    }
    .wrap{width: min(520px, 92vw); text-align:center;}
    .top{
      display:flex;
      align-items:center;
      justify-content:center;
      gap:12px;
      margin-bottom:18px;
      color:#243a57;
      font-weight:600;
      letter-spacing:.2px;
    }
    .dot{
      width:26px;height:26px;border-radius:50%;
      background: linear-gradient(135deg, #9bbcff, #b8a7ff);
      box-shadow: 0 8px 20px rgba(78, 123, 255, .25);
    }
    .card{
      background:var(--card);
      border-radius:var(--radius);
      box-shadow:var(--shadow);
      padding:34px 34px 28px;
    }
    h1{
      margin:0 0 10px;
      font-size:26px;
      color:#2b4b73;
    }
   p{
      margin:0 0 22px;
      color:var(--muted);
      font-size:14px;
      line-height:1.45;
    }
    .field{
      width:100%;
      margin:12px 0;
      text-align:left;
    }
    label{
      display:block;
      font-size:12px;
      color:#52647d;
      margin:0 0 6px;
    }
    input[type="file"], select{
      width:100%;
      padding:11px 12px;
      border:1px solid #d7e0ee;
      border-radius:10px;
      background:#fbfcff;
      font-size:14px;
    }
    .hint{
      margin-top:10px;
      font-size:12px;
      color:#7a8aa3;
      text-align:center;
    }
    button{
      width:100%;
      margin-top:18px;
      padding:12px 14px;
      border:none;
      border-radius:999px;
      background: linear-gradient(180deg, var(--primary), var(--primary2));
      color:white;
      font-weight:600;
      font-size:15px;
      cursor:pointer;
      box-shadow: 0 12px 25px rgba(42, 101, 146, .22);
    }
    button:disabled{
      opacity:.6;
      cursor:not-allowed;
    }
    #status{
      margin-top:18px;
      min-height:22px;
      font-size:13px;
      font-weight:600;
    }
    .ok{color:var(--ok)}
    .err{color:var(--danger)}
    .row{
      display:flex;
      gap:10px;
    }
    .row > *{flex:1}
  </style>
</head>

<body>
  <div class="wrap">
    <div class="top">
      <div class="dot"></div>
      <div>Cloud File Converter</div>
    </div>

    <div class="card">
      <h1>Smart Cloud Converter</h1>
      <p>
        Upload a Word (.docx) or PDF (.pdf) file.
        Choose the conversion direction and download the result.
      </p>

      <form id="form">
        <div class="field">
          <label for="fileInput">File</label>
          <input id="fileInput" name="file" type="file" accept=".pdf,.docx" required />
        </div>

        <div class="field">
          <label for="mode">Convert</label>
          <select id="mode">
            <option value="docx2pdf">Word → PDF</option>
            <option value="pdf2docx">PDF → DOCX</option>
          </select>
        </div>
        
        <div class="hint">
          Supported conversions: Word → PDF | PDF → DOCX
        </div>

        <button id="btn" type="submit">Upload & Convert</button>
        <div id="status"></div>
      </form>
    </div>
  </div>

<script>
  const form = document.getElementById("form");
  const fileInput = document.getElementById("fileInput");
  const mode = document.getElementById("mode");
  const btn = document.getElementById("btn");
  const statusEl = document.getElementById("status");

  function setStatus(msg, type){
    statusEl.className = type ? type : "";
    statusEl.textContent = msg;
  }

  function downloadBlob(blob, filename) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  }

  // Optional: auto-pick mode based on file extension
  fileInput.addEventListener("change", () => {
    const f = fileInput.files[0];
    if (!f) return;
    const name = f.name.toLowerCase();
    if (name.endsWith(".pdf")) mode.value = "pdf2docx";
    if (name.endsWith(".docx")) mode.value = "docx2pdf";
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const f = fileInput.files[0];
    if (!f) { setStatus("Pick a file.", "err"); return; }

    const m = mode.value;

    // Basic validation so user doesn't pick wrong combo
    const name = f.name.toLowerCase();
    if (m === "docx2pdf" && !name.endsWith(".docx")) {
      setStatus("For Word → PDF you must upload a .docx file.", "err");
      return;
    }
    if (m === "pdf2docx" && !name.endsWith(".pdf")) {
      setStatus("For PDF → DOCX you must upload a .pdf file.", "err");
      return;
    }

    const endpoint = (m === "docx2pdf") ? "/docx2pdf" : "/pdf2docx";
    const outName = (m === "docx2pdf") ? "converted.pdf" : "converted.docx";

    const fd = new FormData();
    fd.append("file", f);

    btn.disabled = true;
    setStatus("Converting... please wait.", "");

    try {
      // IMPORTANT: use same-origin (no hardcoded IP) to avoid CORS / Failed to fetch
      const resp = await fetch(endpoint, { method: "POST", body: fd });

      if (!resp.ok) {
        const txt = await resp.text();
        throw new Error(txt || ("HTTP " + resp.status));
      }

      const blob = await resp.blob();
      downloadBlob(blob, outName);
      setStatus("Done. Download started.", "ok");
    } catch (err) {
      setStatus("Error: " + err.message, "err");
    } finally {
      btn.disabled = false;
    }
  });
</script>
</body>
</html>

"""

# ---------- Basic routes ----------
@app.get("/")
def home():
    return render_template_string(HOME_HTML)

@app.get("/health")
def health():
    return jsonify(status="ok")

@app.get("/favicon.ico")
def favicon():
    return ("", 204)

# ---------- Helpers ----------
def upload_to_s3(file_path: str, bucket_name: str, object_key: str):
    s3 = boto3.client("s3")
    s3.upload_file(file_path, bucket_name, object_key)
def docx_to_pdf(input_docx: str, output_pdf: str):
    out_dir = os.path.dirname(output_pdf)
    os.makedirs(out_dir, exist_ok=True)

    # LibreOffice writes output with same base name into out_dir
    cmd = [
        "soffice", "--headless", "--nologo", "--nofirststartwizard",
        "--convert-to", "pdf",
        "--outdir", out_dir,
        input_docx
    ]
    subprocess.check_call(cmd)

    produced = os.path.join(out_dir, os.path.splitext(os.path.basename(input_docx))[0] + ".pdf")
    if produced != output_pdf:
        os.replace(produced, output_pdf)


def pdf_to_docx(input_pdf: str, output_docx: str):
    out_dir = os.path.dirname(output_docx)
    os.makedirs(out_dir, exist_ok=True)

    cv = Converter(input_pdf)
    cv.convert(output_docx, start=0, end=None)
    cv.close()


    subprocess.check_call(cmd)

    # LibreOffice names output based on input filename
    produced = os.path.join(out_dir, os.path.splitext(os.path.basename(input_pdf))[0] + ".docx")
    if not os.path.exists(produced):
        raise RuntimeError("LibreOffice did not produce a DOCX output")

    # rename to the exact path we want
    if produced != output_docx:
        os.replace(produced, output_docx)
# ---------- Browser endpoints ----------
@app.post("/docx2pdf")
def route_docx2pdf():
    f = request.files.get("file")
    if not f or not f.filename:
        return "No file selected", 400
    if not f.filename.lower().endswith(".docx"):
        return "Only .docx files are supported", 400

    base = uuid.uuid4().hex
    input_path = os.path.join(INPUT_DIR, f"{base}.docx")
    output_path = os.path.join(OUTPUT_DIR, f"{base}.pdf")

    f.save(input_path)

    try:
        docx_to_pdf(input_path, output_path)
    except Exception as e:
        return f"Conversion failed: {e}", 500

    return send_file(output_path, as_attachment=True, download_name="converted.pdf")


@app.post("/pdf2docx")
def pdf2docx_ui():
    if "file" not in request.files:
        return "Missing upload field: file", 400

    f = request.files["file"]
    if not f.filename or not f.filename.lower().endswith(".pdf"):
        return "Only PDF files are supported", 400

    base = uuid.uuid4().hex

    input_pdf = os.path.join(INPUT_DIR, f"{base}.pdf")
    output_docx = os.path.join(OUTPUT_DIR, f"{base}.docx")

    # Save uploaded PDF
    f.save(input_pdf)

    try:
        cv = Converter(input_pdf)
        cv.convert(output_docx, start=0, end=None)
        cv.close()
    except Exception as e:
        return f"PDF → DOCX failed: {e}", 500

    if not os.path.exists(output_docx):
        return "DOCX not created", 500

    return send_file(
        output_docx,
        as_attachment=True,
        download_name="converted.docx"
    )


# ---------- AWS/Lambda trigger endpoint (DOCX from S3 → PDF to S3) ----------
@app.post("/<string:filename>")
def aws_docx_trigger(filename):
    try:
        s3 = boto3.client("s3")

        docx_name = f"{filename}.docx"
        pdf_name = f"{filename}.pdf"

        local_docx = os.path.join(INPUT_DIR, docx_name)
        local_pdf  = os.path.join(OUTPUT_DIR, pdf_name)

        s3.download_file(UPLOADS_BUCKET, docx_name, local_docx)
        docx_to_pdf(local_docx, local_pdf)
        upload_to_s3(local_pdf, OUTPUT_BUCKET, pdf_name)

        return jsonify(
            message="Converted and uploaded successfully",
            input_bucket=UPLOADS_BUCKET,
            output_bucket=OUTPUT_BUCKET,
            input_key=docx_name,
            output_key=pdf_name,
        )

    except Exception as e:
        return jsonify(error=str(e)), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)



