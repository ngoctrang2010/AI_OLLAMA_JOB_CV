from flask import Flask, request, jsonify
import chromadb
from sentence_transformers import SentenceTransformer

app = Flask(__name__)

# Khởi tạo ChromaDB client
chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection(name="job_embeddings")

# Load mô hình tạo embedding
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

@app.route('/process_data', methods=['POST'])
def process_data():
    data = request.json  # Nhận dữ liệu JSON

    if not data or not data.get("success"):
        return jsonify({"error": "Dữ liệu không hợp lệ"}), 400

    job_data = data["data"]

    # Xử lý ViTriLamViec
    for idx, position in enumerate(job_data.get("viTriLamViecs", [])):
        text = f"{position.get('viTriTuyenDung', 'No description')} - {position.get('lamViecTai', 'No location')}"
        embedding = embedding_model.encode(text).tolist()
        collection.add(
            ids=[f"position_{idx}"],
            embeddings=[embedding],
            documents=[text]
        )

    # Xử lý CvUngVien
    for idx, cv in enumerate(job_data.get("cvUngViens", [])):
        text = f"{cv.get('viTriUngTuyen', 'No position')} - {cv.get('hocVan', 'No education')} - {cv.get('kinhNghiem', 'No experience')}"
        embedding = embedding_model.encode(text).tolist()
        collection.add(
            ids=[f"cv_{idx}"],
            embeddings=[embedding],
            documents=[text]
        )

    # Xử lý CongViec
    for idx, job in enumerate(job_data.get("congViecs", [])):
        text = f"{job.get('tenCongViec', 'No title')} - {job.get('moTaCongViec', 'No description')} - {job.get('yeuCauCongViec', 'No requirements')}"
        embedding = embedding_model.encode(text).tolist()
        collection.add(
            ids=[f"job_{idx}"],
            embeddings=[embedding],
            documents=[text]
        )

    return jsonify({"message": "Dữ liệu đã được chuyển thành embedding và lưu vào ChromaDB"}), 200

@app.route('/list_data', methods=['GET'])
def list_data():
    results = collection.get(include=['documents', 'embeddings', 'metadatas'])
    return jsonify({
        "count": len(results["documents"]),
        "documents": results["documents"],
        "ids": results["ids"]
    })

if __name__ == '__main__':
    app.run(port=5000, debug=True)
