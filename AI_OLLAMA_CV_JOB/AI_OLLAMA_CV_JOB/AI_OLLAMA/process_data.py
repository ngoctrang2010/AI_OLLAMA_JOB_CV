from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer
from chromadb import PersistentClient
import os
import numpy as np

app = Flask(__name__)
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
os.environ["CHROMA_DB_PATH"] = "./wwwroot/Chroma_data/chroma.sqlite" 

client = PersistentClient(
    path="./wwwroot/Chroma_data"
)

def format_congviec(cv):
    return f"{cv.get('Id', '')} | {cv.get('IdNtd', '')} | {cv.get('TenCongViec', '')} | {cv.get('MoTaCongViec', '')} | {cv.get('YeuCauCongViec', '')} | {cv.get('PhucLoi', '')} | {cv.get('DiaDiemThoiGian', '')} | {cv.get('CachThucUngTuyen', '')} | {cv.get('KinhNghiem', '')} | {cv.get('MucLuong', '')} | {cv.get('HanNop', '')} | {cv.get('HocVan', '')}"

def format_cvungvien(cv):
    return f"{cv.get('Id', '')} | {cv.get('ViTriUngTuyen', '')} | {cv.get('HocVan', '')} | {cv.get('KinhNghiem', '')} | {cv.get('DuAn', '')} | {cv.get('ChungChi', '')} | {cv.get('IdUngVien', '')}"

def format_vitri(vt):
    return f"{vt.get('Id', '')} | {vt.get('IdUngVien', '')} | {vt.get('ViTriTuyenDung', '')} | {vt.get('LamViecTai', '')} | {vt.get('HinhThucLamViec', '')} | {vt.get('TrinhDo', '')} | {vt.get('MucLuong', '')} | {vt.get('HocVan','')}"

def embed_data(list_data, prefix, format_func):
    try:
        collection = client.get_collection(prefix)
    except:
        collection = client.create_collection(prefix) 

    new_data = []
    for item in list_data:
        text = format_func(item)
        if not text.strip():
            continue
        emb = model.encode(text).tolist()
        new_data.append({
            "id": f"{item['Id']}",
            "document": text,
            "embedding": emb
        })

    if new_data:
        collection.add(
            ids=[data["id"] for data in new_data],
            embeddings=[data["embedding"] for data in new_data],
            metadatas=[{"document": data["document"], "id": data["id"]} for data in new_data]
        )

    return new_data

@app.route('/process-data', methods=['POST'])
def process_data():
    payload = request.json or {}
    cong = payload.get('CongViecs', [])
    cv = payload.get('CvUngViens', [])
    vt = payload.get('ViTriLamViecs', [])

    congviec_embeddings = embed_data(cong, 'CongViec_Collection', format_congviec)
    cvungvien_embeddings = embed_data(cv, 'CvUngVien_Collection', format_cvungvien)
    vitri_embeddings = embed_data(vt, 'ViTriUngTuyen_Collection', format_vitri)

    return jsonify({
        "status": "success",
        "congviec_embeddings": congviec_embeddings,
        "cvungvien_embeddings": cvungvien_embeddings,
        "vitri_embeddings": vitri_embeddings
    })

@app.route('/view-data', methods=['GET'])
def view_data():
    collections = client.list_collections()
    data_summary = {}

    for collection in collections:
        try:
            data = collection.get(include=["metadatas", "embeddings"])
            print("Raw Data:", data)  # In ra dữ liệu để kiểm tra
            data_summary[collection.name] = [
                {
                    "document": doc.get("document", "No document"),
                    "embedding_sample": list(embedding[:3]) if isinstance(embedding, (list, np.ndarray)) else "No embedding"
                }
                for doc, embedding in zip(data.get("metadatas", []), data.get("embeddings", []))
            ]
        except Exception as e:
            data_summary[collection.name] = f"Error retrieving data: {str(e)}"

    print("Formatted Data:", data_summary)  # In ra dữ liệu đã được format
    return jsonify(data_summary)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
