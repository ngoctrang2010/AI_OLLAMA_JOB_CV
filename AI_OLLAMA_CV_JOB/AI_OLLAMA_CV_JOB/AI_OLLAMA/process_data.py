from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer
from chromadb import PersistentClient
import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import requests


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

def get_data_Chroma():
    collections = client.list_collections()
    data_summary = {}

    for collection in collections:
        try:
            data = collection.get(include=["metadatas", "embeddings"])
            data_summary[collection.name] = [
                {
                    "document": doc.get("document", "No document"),
                    "embedding_sample": list(embedding[:3]) if isinstance(embedding, (list, np.ndarray)) else "No embedding"
                }
                for doc, embedding in zip(data.get("metadatas", []), data.get("embeddings", []))
            ]
        except Exception as e:
            data_summary[collection.name] = f"Error retrieving data: {str(e)}"

    return data_summary

@app.route('/view-data', methods=['GET'])
def view_data():
    data_summary = get_data_Chroma()
    return jsonify(data_summary)

@app.route('/qa', methods=['GET'])
def question_asked():
    question = request.args.get("question", "Lập trình Mobile")
    if not question.strip():
        return jsonify({"error": "Câu hỏi không được để trống."}), 400

    try:
        question_emb = model.encode(question).tolist()
    except Exception as e:
        return jsonify({"error": f"Không thể mã hóa câu hỏi: {str(e)}"}), 500

    results = []

    try:
        collections = client.list_collections()

        for collection in collections:
            try:
                query_result = collection.query(
                    query_embeddings=[question_emb],
                    n_results=5,
                    include=["metadatas", "distances"]
                )

                documents = query_result.get("metadatas", [[]])[0]
                distances = query_result.get("distances", [[]])[0]

                collection_results = [
                    {
                        "collection": collection.name,
                        "document": doc.get("document", "No document"),
                        "similarity": round(1 - dist, 4)
                    }
                    for doc, dist in zip(documents, distances)
                ]

                results.extend(collection_results)

            except Exception as e:
                print(f"Lỗi khi truy vấn collection {collection.name}: {e}")

    except Exception as e:
        return jsonify({"error": f"Lỗi khi lấy danh sách collections: {str(e)}"}), 500

    return jsonify({"results": results})



@app.route('/ask-ai', methods=['GET'])
def ask_ai():
    question = request.args.get("question", "")
    if not question.strip():
        return jsonify({"error": "Missing question"}), 400

    try:
        question_emb = model.encode(question).tolist()
    except Exception as e:
        return jsonify({"error": f"Không thể mã hóa câu hỏi: {str(e)}"}), 500

    results = []

    try:
        collections = client.list_collections()

        for collection in collections:
            try:
                query_result = collection.query(
                    query_embeddings=[question_emb],
                    n_results=7,
                    include=["metadatas", "distances"]
                )

                documents = query_result.get("metadatas", [[]])[0]
                distances = query_result.get("distances", [[]])[0]

                collection_results = [
                    {
                        "collection": collection.name,
                        "document": doc.get("document", "No document"),
                        "similarity": round(1 - dist, 4)
                    }
                    for doc, dist in zip(documents, distances)
                ]

                results.extend(collection_results)

            except Exception as e:
                print(f"Lỗi khi truy vấn collection {collection.name}: {e}")

    except Exception as e:
        return jsonify({"error": f"Lỗi khi lấy danh sách collections: {str(e)}"}), 500

    context = "\n".join([f"- {item['document']}" for item in results])

    prompt = f"""
        Dưới đây là các thông tin công việc được tìm thấy gần giống nhất với câu hỏi. Hãy đọc kỹ và trả lời câu hỏi cuối cùng:

        Thông tin công việc:
        {context}

        Câu hỏi của tôi: {question}

        Hãy trả lời tôi bằng tiếng Việt nhé bạn, nội dung bạn trả lời phải như 1 văn bản. Các kết quả bạn trả lời hãy chia nhóm.
        """

    try:
        ollama_response = requests.post("http://localhost:11434/api/generate", json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        })
        answer = ollama_response.json().get("response", "Không có phản hồi từ mô hình.")
    except Exception as e:
        return jsonify({"error": f"Lỗi khi gọi Ollama API: {str(e)}"}), 500

    return jsonify({"question": question, "answer": answer, "context": results})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
