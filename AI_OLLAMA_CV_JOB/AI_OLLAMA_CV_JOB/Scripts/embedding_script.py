import pyodbc
import chromadb
from sentence_transformers import SentenceTransformer

# Kết nối SQL Server
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};SERVER=ALBERT\\SQLEXPRESS;DATABASE=AI_OLLAMA_CV_JOB;Trusted_Connection=yes;Encrypt=no'
)
cursor = conn.cursor()

# Lấy dữ liệu từ bảng CongViec
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
rows = cursor.fetchall()

# Load mô hình embedding local
model = SentenceTransformer('all-MiniLM-L6-v2')

# Kết nối Chroma
chroma_client = chromadb.PersistentClient(path="./chroma_data")
collection = chroma_client.get_or_create_collection("cv_vectors")

# Tạo embedding và lưu
for row in rows:
    cv_id = str(row.Id)
    text = row.CleanText
    embedding = model.encode(text).tolist()
    collection.add(
        ids=[cv_id],
        embeddings=[embedding],
        documents=[text]
    )

# Lấy lại dữ liệu đã lưu: id, document, embedding
results = collection.get(include=["documents", "embeddings"])

# Ghi dữ liệu ra file
with open("saved_data.txt", "w", encoding="utf-8") as f:
    for doc_id, doc_text, embedding in zip(results['ids'], results['documents'], results['embeddings']):
        # Cắt text cho gọn, lấy embedding 5 giá trị đầu tiên làm mẫu
        short_text = doc_text[:200].replace('\n', ' ').replace('\r', ' ')
        short_embedding = embedding[:5]
        f.write(f"{doc_id}: {short_text}...\nEmbedding (5 đầu tiên): {short_embedding}\n\n")

print("Thanh cong.")
