import pyodbc
import chromadb
from sentence_transformers import SentenceTransformer
import sys
import io

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
    SELECT TOP 1000 Id, CONCAT(
        TenCongViec, ' ',
        MoTaCongViec, ' ',
        YeuCauCongViec, ' ',
        PhucLoi, ' ',
        DiaDiem_ThoiGian, ' ',
        CachThucUngTuyen, ' ',
        KinhNghiem, ' ',
        MucLuong, ' ',
        HanNop
    ) AS CleanText
    FROM CongViec
    WHERE MoTaCongViec IS NOT NULL AND YeuCauCongViec IS NOT NULL
""")
rows_cv = cursor.fetchall()

for row in rows_cv:
    cv_id = str(row.Id)
    text = row.CleanText
    embedding = model.encode(text).tolist()
    collection_cv.add(
        ids=[cv_id],
        embeddings=[embedding],
        metadatas=[{"id": cv_id, "document": text}]  # Lưu văn bản gốc vào metadata
    )

print(f"Đã lưu {len(rows_cv)} vector CongViec.")


# ====== 2️⃣ Xử lý bảng UngVien ======
print("Embedding UngVien...")
collection_uv = chroma_client.get_or_create_collection("ungvien_vectors")

cursor.execute("""
    SELECT TOP 1000 Id, CONCAT(
        HoTen, ' ',
        Email, ' ',
        DuongdanCV, ' ',
        KyNang, ' ',
        SDT
    ) AS CleanText
    FROM UngVien
    WHERE KyNang IS NOT NULL
""")
rows_uv = cursor.fetchall()

for row in rows_uv:
    uv_id = str(row.Id)
    text = row.CleanText
    embedding = model.encode(text).tolist()
    collection_uv.add(
        ids=[uv_id],
        embeddings=[embedding],
        metadatas=[{"id": uv_id, "document": text}]  # Lưu văn bản gốc vào metadata
    )

print(f"Đã lưu {len(rows_uv)} vector UngVien.")


# ====== 3️⃣ Xử lý bảng CV_UngVien ======
print("Embedding CV_UngVien...")
collection_cvuv = chroma_client.get_or_create_collection("cv_ungvien_vectors")

cursor.execute("""
    SELECT TOP 1000 Id, CONCAT(
        ViTriUngTuyen, ' ',
        HocVan, ' ',
        KinhNghiem, ' ',
        DuAn, ' ',
        ChungChi
    ) AS CleanText
    FROM CV_UngVien
    WHERE ViTriUngTuyen IS NOT NULL
""")
rows_cvuv = cursor.fetchall()

for row in rows_cvuv:
    cvuv_id = str(row.Id)
    text = row.CleanText
    embedding = model.encode(text).tolist()
    collection_cvuv.add(
        ids=[cvuv_id],
        embeddings=[embedding],
        metadatas=[{"id": cvuv_id, "document": text}]  # Lưu văn bản gốc vào metadata
    )

print(f"Đã lưu {len(rows_cvuv)} vector CV_UngVien.")





# ====== Ghi file kết quả ======
with open("saved_vectors_with_ids.txt", "w", encoding="utf-8") as f:
    # Ghi CongViec
    results_cv = collection_cv.get(include=["embeddings", "metadatas"])
    f.write("=== CongViec ===\n")
    for doc_id, embedding, metadata in zip(results_cv['ids'], results_cv['embeddings'], results_cv['metadatas']):
        f.write(f"{doc_id}: Embedding: {embedding}, Metadata: {metadata['document']}\n")  # Lấy văn bản gốc từ metadata
    f.write("\n")

    # Ghi UngVien
    results_uv = collection_uv.get(include=["embeddings", "metadatas"])
    f.write("=== UngVien ===\n")
    for doc_id, embedding, metadata in zip(results_uv['ids'], results_uv['embeddings'], results_uv['metadatas']):
        f.write(f"{doc_id}: Embedding: {embedding}, Metadata: {metadata['document']}\n")  # Lấy văn bản gốc từ metadata
    f.write("\n")

    # Ghi CV_UngVien
    results_cvuv = collection_cvuv.get(include=["embeddings", "metadatas"])
    f.write("=== CV_UngVien ===\n")
    for doc_id, embedding, metadata in zip(results_cvuv['ids'], results_cvuv['embeddings'], results_cvuv['metadatas']):
        f.write(f"{doc_id}: Embedding: {embedding}, Metadata: {metadata['document']}\n")  # Lấy văn bản gốc từ metadata
    f.write("\n")

print("Đã lưu toàn bộ vector và văn bản gốc thành công.")
