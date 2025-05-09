
from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer
from chromadb import PersistentClient
import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import requests
from concurrent.futures import ThreadPoolExecutor
from flask_cors import CORS


app = Flask(__name__)
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
os.environ["CHROMA_DB_PATH"] = "./wwwroot/Chroma_data/chroma.sqlite" 
CORS(app)
client = PersistentClient(
    path="./wwwroot/Chroma_data"
)
@app.route('/delete-all-data', methods=['GET'])
def delete_all_data():
    try:
        delete_all_collections()  # Gọi hàm xóa dữ liệu
        return jsonify({"status": "success", "message": "Đã xóa toàn bộ dữ liệu trong Chroma."}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

def delete_all_collections():
    collections = client.list_collections()
    for collection in collections:
        client.delete_collection(collection.name)

def format_congviec(cv):
    return (
        f"🔹 ID: {cv.get('Id', '')}\n"
        f"🔹 Tên công việc: {cv.get('TenCongViec', '')}\n"
        f"🔹 Mô tả công việc: {cv.get('MoTaCongViec', '')}\n"
        f"🔹 Yêu cầu công việc: {cv.get('YeuCauCongViec', '')}\n"
        f"🔹 Phúc lợi: {cv.get('PhucLoi', '')}\n"
        f"🔹 Địa điểm làm việc: {cv.get('DiaDiem', '')}\n"
        f"🔹 Thời gian làm việc: {cv.get('ThoiGianLamViec', '')}\n"
        f"🔹 Cách thức ứng tuyển: {cv.get('CachThucUngTuyen', '')}\n"
        f"🔹 Mức lương: {cv.get('MucLuong', '')}\n"
        f"🔹 Hạn nộp: {cv.get('HanNop', '')}\n"
        f"🔹 Trình độ học vấn: {cv.get('TrinhDoHocVan', '')}\n"
        f"🔹 Yêu cầu kinh nghiệm: {cv.get('YeuCauKinhNghiem', '')}\n"
        f"🔹 Công ty: {cv.get('TenCty', '')}"
    ).strip()


def format_cvungvien(cv):
    return (
        f"🔹 ID: {cv.get('Id', '')}\n"
        f"🔹 Tên ứng viên: {cv.get('HoTen', '')}\n"
        f"🔹 Vị trí ứng tuyển 1: {cv.get('ViTriUngTuyen1', '')}\n"
        f"🔹 Vị trí ứng tuyển 2: {cv.get('ViTriUngTuyen2', '')}\n"
        f"🔹 Học vấn: {cv.get('TrinhDoHocVan', '')}\n"
        f"🔹 Kinh nghiệm làm việc: {cv.get('KinhNghiemLamViec', '')}\n"
        f"🔹 Dự án: {cv.get('DuAn', '')}\n"
        f"🔹 Chứng chỉ: {cv.get('ChungChi', '')}\n"
        f"🔹 Tìm việc tại: {cv.get('TimViecTai', '')}\n"
        f"🔹 Hình thức làm việc: {cv.get('HinhThucLamViec', '')}\n"
        f"🔹 Mức lương: {cv.get('MucLuong', '')}\n"
        f"🔹 Link CV: {cv.get('DuongDanCV', '')}"
    ).strip()
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

    ungvien_list = payload.get('Data_UngVien_Chroma', [])
    congviec_list = payload.get('Data_CongViec_Chroma', [])

    cvungvien_embeddings = embed_data(ungvien_list, 'CvUngVien_Collection', format_cvungvien)
    congviec_embeddings = embed_data(congviec_list, 'CongViec_Collection', format_congviec)

    return jsonify({
        "status": "success",
        "cvungvien_embeddings": cvungvien_embeddings,
        "congviec_embeddings": congviec_embeddings
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

    # Mã hóa câu hỏi
    try:
        question_emb = model.encode(question).tolist()
    except Exception as e:
        return jsonify({"error": f"Không thể mã hóa câu hỏi: {str(e)}"}), 500

    # Lấy danh sách collections
    try:
        collections = client.list_collections()
    except Exception as e:
        return jsonify({"error": f"Lỗi khi lấy danh sách collections: {str(e)}"}), 500

    results = []

    def query_collection(collection):
        try:
            result = collection.query(
                query_embeddings=[question_emb],
                n_results=10,
                include=["metadatas", "distances"]
            )
            documents = result.get("metadatas", [[]])[0]
            distances = result.get("distances", [[]])[0]
            return [
                {
                    "collection": collection.name,
                    "document": doc.get("document", "No document"),
                    "similarity": round(1 - dist, 4)
                }
                for doc, dist in zip(documents, distances)
                if dist < 8  # loại bỏ similarity âm hoặc rất thấp
            ]
        except Exception as e:
            print(f"Lỗi khi truy vấn collection {collection.name}: {e}")
            return []

    # Truy vấn song song
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(query_collection, col) for col in collections]
        for future in futures:
            results.extend(future.result())

    # Lấy top 10 kết quả theo độ tương đồng
    top_results = sorted(results, key=lambda x: x["similarity"], reverse=True)[:10]

    # Gom nhóm kết quả theo collection
    grouped = {
        "CongViec_Collection": [],
        "CvUngVien_Collection": [],
        "ViTriUngTuyen_Collection": []
    }
    for item in top_results:
        if item["collection"] in grouped:
            grouped[item["collection"]].append(item["document"])

    # Format context rõ ràng
    context_parts = {
        "CongViec_Collection": "\n".join(f"- {doc}" for doc in grouped["CongViec_Collection"]) or "- Không có dữ liệu phù hợp",
        "CvUngVien_Collection": "\n".join(f"- {doc}" for doc in grouped["CvUngVien_Collection"]) or "- Không có dữ liệu phù hợp",
        "ViTriUngTuyen_Collection": "\n".join(f"- {doc}" for doc in grouped["ViTriUngTuyen_Collection"]) or "- Không có dữ liệu phù hợp"
    }
    # Prompt tối ưu, hướng dẫn LLM trả lời chính xác

    prompt = f"""
        📌 Bạn là một trợ lý ảo thân thiện của trang web tuyển dụng **JobOne**, tên là **JobOneAgent**, chuyên hỗ trợ người dùng trong hệ thống tuyển dụng trực tuyến.

        🎯 **Nguyên tắc trả lời:**

            1. **Chào hỏi, hỏi thăm:**
               - Trả lời thân thiện, tự nhiên, mang tính cá nhân.

            2. **Câu hỏi về tuyển dụng (công việc, CV, vị trí, công ty):**
               - Không dịch **tên công việc, vị trí, công ty**.
               - Nếu người dùng là **nhà tuyển dụng**: tìm **ứng viên phù hợp** với yêu cầu công việc.
               - Nếu người dùng là **ứng viên**: tìm **việc làm phù hợp** với CV hoặc nguyện vọng.
               - Có thể **đề xuất thêm tối đa 5 công việc phù hợp**.

            3. **Câu hỏi về công ty:**
               - Trả lời dựa trên thông tin công ty có trong hệ thống (nếu có).

            4. **Câu hỏi khác hoặc không rõ ràng:**
               - Trả lời lịch sự và hướng dẫn người dùng sử dụng hệ thống để tìm thông tin chính xác.

            5. **Lưu ý quan trọng:**
               - **KHÔNG SUY ĐOÁN, BIẾN TẤU HAY TỰ THAY ĐỔI DỮ LIỆU CỦA HỆ THỐNG.**
               - **KHÔNG HIỂN THỊ THÔNG TIN NHẠY CẢM NHƯ ID.**
               - Khi liệt kê, trình bày dưới dạng danh sách rõ ràng.
               - Khi hiển thị danh sách công việc, dùng mẫu: `Tên công việc – Làm việc tại – Mô tả – Mức lương – Cách thức ứng tuyển`
               - Khi hiển thị danh sách CV ứng viên, dùng mẫu: `Tên ứng viên – Vị trí ứng tuyển – Học vấn – Kinh nghiệm – Link CV`
               - Ưu tiên dữ liệu theo thứ tự:
                    Độ ưu tiên 1: Tìm việc tại, địa điểm làm việc
                    Độ ưu tiên 2: Tên công việc, vị trí ứng tuyển
                    Độ ưu tiên 3: Kinh nghiệm, học vấn
                    Độ ưu tiên 4: Mức lương và thông tin khác
               
               - Không đề cập đến các trang tuyển dụng khác.

        📊 **Dữ liệu hệ thống:**

            1. 🧾 **Công việc đang tuyển (dùng để gợi ý):**
               {context_parts["CongViec_Collection"]}

            2. 📄 **CV ứng viên (dùng để tìm ứng viên phù hợp):**
               {context_parts["CvUngVien_Collection"]}

         ---

        ❓ **Câu hỏi của người dùng:** {question}

        📌 **Yêu cầu phản hồi bằng tiếng Việt. Tên công ty hoặc công việc giữ nguyên (không dịch). Trả lời ngắn gọn, rõ ràng và đúng mục tiêu.**
    """.strip()

    # Gọi mô hình Ollama
    try:
        print(prompt)
        ollama_response = requests.post("http://localhost:11434/api/generate", json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        })
        answer = ollama_response.json().get("response", "Không có phản hồi từ mô hình.")
    except Exception as e:
        return jsonify({"error": f"Lỗi khi gọi Ollama API: {str(e)}"}), 500

    return jsonify({
        "answer": answer
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
