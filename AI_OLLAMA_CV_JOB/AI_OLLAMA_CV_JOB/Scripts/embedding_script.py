from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel, ValidationError
from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer
import fitz  # PyMuPDF
import chromadb
import pyodbc
import requests
import sys
import io 
import os


# Fix Unicode lỗi console Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Kết nối SQL Server
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};SERVER=ALBERT\\SQLEXPRESS;DATABASE=AI_OLLAMA_CV_JOB;Trusted_Connection=yes;Encrypt=no'
)
cursor = conn.cursor()

# Load mô hình embedding local
model = SentenceTransformer('all-MiniLM-L6-v2')

# Kết nối Chroma
chroma_client = chromadb.PersistentClient(path="./chroma_data")




# ====== 1️⃣ Xử lý bảng CongViec ======
print("Embedding CongViec...")
collection_cv = chroma_client.get_or_create_collection("cv_vectors")

cursor.execute("""
    SELECT TOP 1000 Id, TenCongViec, MoTaCongViec, YeuCauCongViec, PhucLoi, DiaDiem_ThoiGian, CachThucUngTuyen, KinhNghiem, MucLuong, HanNop
    FROM CongViec
    WHERE MoTaCongViec IS NOT NULL AND YeuCauCongViec IS NOT NULL
""")
rows_cv = cursor.fetchall()

for row in rows_cv:
    cv_id = str(row.Id)
    text = f"""Tên công việc: {row.TenCongViec};
Mô tả công việc: {row.MoTaCongViec};
Yêu cầu công việc: {row.YeuCauCongViec};
Phúc lợi: {row.PhucLoi};
Địa điểm & Thời gian: {row.DiaDiem_ThoiGian};
Cách thức ứng tuyển: {row.CachThucUngTuyen};
Kinh nghiệm: {row.KinhNghiem};
Mức lương: {row.MucLuong};
Hạn nộp: {row.HanNop};"""

    embedding = model.encode(text).tolist()
    collection_cv.add(
        ids=[cv_id],
        embeddings=[embedding],
        documents=[text],
        metadatas=[{"id": cv_id, "document": text}]
    )

print(f"✅ Đã lưu {len(rows_cv)} vector CongViec.")


# ====== 2️⃣ Xử lý bảng UngVien ======
print("Embedding UngVien...")
collection_uv = chroma_client.get_or_create_collection("ungvien_vectors")

cursor.execute("""
    SELECT TOP 1000 Id, HoTen, Email, DuongdanCV, KyNang, SDT
    FROM UngVien
    WHERE KyNang IS NOT NULL
""")
rows_uv = cursor.fetchall()

for row in rows_uv:
    uv_id = str(row.Id)
    text = f"""Họ tên: {row.HoTen};
Email: {row.Email};
Đường dẫn CV: {row.DuongdanCV};
Kỹ năng: {row.KyNang};
Số điện thoại: {row.SDT};"""

    embedding = model.encode(text).tolist()
    collection_uv.add(
        ids=[uv_id],
        embeddings=[embedding],
        metadatas=[{"id": uv_id, "document": text}]
    )

print(f"✅ Đã lưu {len(rows_uv)} vector UngVien.")


# ====== 3️⃣ Xử lý bảng CV_UngVien ======
print("Embedding CV_UngVien...")
collection_cvuv = chroma_client.get_or_create_collection("cv_ungvien_vectors")

cursor.execute("""
    SELECT TOP 1000 Id, ViTriUngTuyen, HocVan, KinhNghiem, DuAn, ChungChi
    FROM CV_UngVien
    WHERE ViTriUngTuyen IS NOT NULL
""")
rows_cvuv = cursor.fetchall()

for row in rows_cvuv:
    cvuv_id = str(row.Id)
    text = f"""Vị trí ứng tuyển: {row.ViTriUngTuyen};
Học vấn: {row.HocVan};
Kinh nghiệm: {row.KinhNghiem};
Dự án: {row.DuAn};
Chứng chỉ: {row.ChungChi};"""

    embedding = model.encode(text).tolist()
    collection_cvuv.add(
        ids=[cvuv_id],
        embeddings=[embedding],
        metadatas=[{"id": cvuv_id, "document": text}]
    )

print(f"✅ Đã lưu {len(rows_cvuv)} vector CV_UngVien.")




# ====== Ghi file kết quả ======
with open("saved_vectors_with_ids.txt", "w", encoding="utf-8") as f:
    # Ghi Công Việc
    results_cv = collection_cv.get(include=["embeddings", "metadatas"])
    f.write("=== CongViec ===\n")
    for doc_id, embedding, metadata in zip(results_cv['ids'], results_cv['embeddings'], results_cv['metadatas']):
        f.write(f"{doc_id}:\n")
        f.write(f"  Metadata: {metadata['document']}\n")
        f.write(f"  Vector: {embedding}\n\n")

    # Ghi Ứng Viên
    results_uv = collection_uv.get(include=["embeddings", "metadatas"])
    f.write("=== UngVien ===\n")
    for doc_id, embedding, metadata in zip(results_uv['ids'], results_uv['embeddings'], results_uv['metadatas']):
        f.write(f"{doc_id}:\n")
        f.write(f"  Metadata: {metadata['document']}\n")
        f.write(f"  Vector: {embedding}\n\n")

    # Ghi CV Ứng Viên
    results_cvuv = collection_cvuv.get(include=["embeddings", "metadatas"])
    f.write("=== CV_UngVien ===\n")
    for doc_id, embedding, metadata in zip(results_cvuv['ids'], results_cvuv['embeddings'], results_cvuv['metadatas']):
        f.write(f"{doc_id}:\n")
        f.write(f"  Metadata: {metadata['document']}\n")
        f.write(f"  Vector: {embedding}\n\n")

print("✅ Đã lưu toàn bộ vector, metadata và văn bản gốc thành công.")


# Khởi tạo FastAPI app
app = FastAPI()
collection = chroma_client.get_or_create_collection(name="noiquy_vectors")
class DocumentData(BaseModel):
    doc_id: str
    company_name: str
    content: str

@app.post("/vectorize/")
async def vectorize_document(data: DocumentData):
    try:
        text = data.content
        vector = model.encode(text).tolist()  # Chuyển nội dung thành vector

        # Lưu vào ChromaDB
        collection.add(
            documents=[text], 
            embeddings=[vector], 
            metadatas=[{"company": data.company_name}], 
            ids=[data.doc_id]
        )

        return {"message": "Vectorization successful", "doc_id": data.doc_id, "company": data.company_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def check_ollama_alive():
    try:
        r = requests.get("http://localhost:11434")
        return r.status_code == 200
    except Exception:
        return False

class QuestionRequest(BaseModel):
    question_text: str
    top_k: int = 5
    model_name: str = 'tinyllama'

@app.post("/ask_question/")
async def ask_question(request: QuestionRequest):
    if not check_ollama_alive():
        raise HTTPException(status_code=503, detail="Ollama server không sẵn sàng.")

    # Bước 1: Encode embedding
    query_embedding = model.encode(request.question_text).tolist()

    # Bước 2: Search trong Chroma
    collection = chroma_client.get_collection("cv_vectors")
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=request.top_k,
        include=["distances", "metadatas", "documents"]
    )

    # Bước 3: Tạo danh sách đề xuất công việc
    recommended_jobs = []
    context_chunks = []
    for idx, doc in enumerate(results['documents'][0]):
        summary = doc[:200] + "..." if len(doc) > 200 else doc
        recommended_jobs.append({
            "id": results['metadatas'][0][idx].get('id', f"job_{idx}"),
            "summary": summary
        })
        context_chunks.append(summary)

    # Bước 4: Chuẩn bị prompt (giới hạn độ dài context)
    max_context_chars = 2000
    context_text = "\n".join(context_chunks)
    if len(context_text) > max_context_chars:
        context_text = context_text[:max_context_chars] + "..."

    final_prompt = (
        f"Các công việc gợi ý dựa trên dữ liệu:\n{context_text}\n\n"
        f"Câu hỏi của ứng viên (bằng tiếng Việt):\n{request.question_text}\n\n"
        f"Hãy chọn công việc phù hợp nhất và giải thích lý do bằng tiếng Việt."
    )

    # Bước 5: Gửi sang Ollama
    ollama_url = "http://localhost:11434/api/generate"
    payload = {
        "model": request.model_name,
        "prompt": final_prompt,
        "stream": False
    }

    try:
        response = requests.post(ollama_url, json=payload, timeout=180)
        response.raise_for_status()
        data = response.json()
        answer = data.get('response', '')
        return {
            "answer": answer,
            "recommended_jobs": recommended_jobs
        }
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi gọi Ollama API: {e}")

# Hàm đọc nội dung từ PDF
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = "\n".join(page.get_text("text") for page in doc)
    return text

@app.post("/extract_text/")
async def extract_text(file: UploadFile = File(...)):
    try:
        # Lưu file tạm
        temp_folder = "./temp"
        os.makedirs(temp_folder, exist_ok=True)
        temp_path = os.path.join(temp_folder, file.filename)
        with open(temp_path, "wb") as temp_file:
            temp_file.write(file.file.read())

        # Trích xuất văn bản từ PDF
        pdf_text = extract_text_from_pdf(temp_path)
        max_chars = 5000
        truncated_text = pdf_text[:max_chars] + "..." if len(pdf_text) > max_chars else pdf_text

        # Tóm tắt bằng Ollama
        final_prompt = f"""
Đây là nội dung một CV xin việc:

{truncated_text}

Hãy đọc kỹ và tóm tắt nội dung chính của CV này bằng tiếng Việt. Bao gồm:
- Họ và tên (nếu có)
- Kỹ năng chính
- Kinh nghiệm làm việc (nếu có)
- Trình độ học vấn
- Các thông tin nổi bật khác.
"""
        ollama_url = "http://localhost:11434/api/generate"
        payload = {
            "model": "tinyllama",
            "prompt": final_prompt,
            "stream": False
        }
        response = requests.post(ollama_url, json=payload)
        response.raise_for_status()
        ollama_summary = response.json().get('response', '').strip()

        # Tạo embedding và truy vấn Chroma
        embedder = SentenceTransformer('all-MiniLM-L6-v2')
        query_vec = embedder.encode(ollama_summary).tolist()
        collection = chroma_client.get_collection("cv_vectors")
        results = collection.query(query_embeddings=[query_vec], n_results=5)

        # Gửi top job docs đến Ollama để đề xuất công việc
        matched_jobs = []
        for doc, metadata in zip(results["documents"][0], results["metadatas"][0]):
            job_prompt = f"""
Đây là bản tóm tắt một CV xin việc:

{ollama_summary}

Và đây là các mô tả công việc phù hợp:

{doc}

Hãy đề xuất công việc phù hợp với cv trình bày rõ ràng thêm cả lý do phù hợp của từng công việc.
"""
            job_payload = {
                "model": "tinyllama",
                "prompt": job_prompt,
                "stream": False
            }
            job_response = requests.post(ollama_url, json=job_payload)
            job_response.raise_for_status()
            match_reason = job_response.json().get("response", "").strip()

            matched_jobs.append({
                "position": metadata.get("position", "Không rõ"),
                "description": doc,
                "suggestion": match_reason
            })

        return {
            "answer": ollama_summary,
            "extracted_text": truncated_text.strip(),
            "matched_jobs": matched_jobs
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi xử lý: {str(e)}")
# Chạy server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)