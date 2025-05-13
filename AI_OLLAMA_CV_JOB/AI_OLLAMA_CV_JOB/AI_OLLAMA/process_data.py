from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer
from chromadb import PersistentClient
import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import requests
from concurrent.futures import ThreadPoolExecutor
from flask_cors import CORS
import json
import uuid
import requests


app = Flask(__name__)
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
os.environ["CHROMA_DB_PATH"] = "./wwwroot/Chroma_data/chroma.sqlite" 
CORS(app)
client = PersistentClient(
    path="./wwwroot/Chroma_data"
)
session = requests.Session()
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
'''
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
'''
def format_congviec_json(cv):
    return {
        "ID": cv.get("Id", ""),
        "TenCongViec": cv.get("TenCongViec", ""),
        "MoTaCongViec": cv.get("MoTaCongViec", ""),
        "YeuCauCongViec": cv.get("YeuCauCongViec", ""),
        "PhucLoi": cv.get("PhucLoi", ""),
        "DiaDiem": cv.get("DiaDiem", ""),
        "ThoiGianLamViec": cv.get("ThoiGianLamViec", ""),
        "CachThucUngTuyen": cv.get("CachThucUngTuyen", ""),
        "MucLuong": cv.get("MucLuong", ""),
        "HanNop": cv.get("HanNop", ""),
        "TrinhDoHocVan": cv.get("TrinhDoHocVan", ""),
        "YeuCauKinhNghiem": cv.get("YeuCauKinhNghiem", ""),
        "TenCongty": cv.get("TenCty", "")
    }
def format_cvungvien_json(cv):
    return {
        "ID": cv.get("Id", ""),
        "HoTen": cv.get("HoTen", ""),
        "ViTriUngTuyen1": cv.get("ViTriUngTuyen1", ""),
        "ViTriUngTuyen2": cv.get("ViTriUngTuyen2", ""),
        "TrinhDoHocVan": cv.get("TrinhDoHocVan", ""),
        "KinhNghiemLamViec": cv.get("KinhNghiemLamViec", ""),
        "DuAn": cv.get("DuAn", ""),
        "ChungChi": cv.get("ChungChi", ""),
        "TimViecTai": cv.get("TimViecTai", ""),
        "HinhThucLamViec": cv.get("HinhThucLamViec", ""),
        "MucLuong": cv.get("MucLuong", ""),
        "DuongDanCV": cv.get("DuongDanCV", "")
    }

def embed_data(list_data, prefix, format_func):
    try:
        collection = client.get_collection(prefix)
        # Lấy danh sách ID đã tồn tại trong collection
        existing_ids = set(collection.get()['ids'])
    except:
        collection = client.create_collection(prefix)
        existing_ids = set()

    new_data = []
    for item in list_data:
        item_id = str(item.get('Id', uuid.uuid4()))
        if item_id in existing_ids:
            continue  # bỏ qua nếu ID đã tồn tại

        formatted_data = format_func(item)
        text = json.dumps(formatted_data, ensure_ascii=False)

        if not text.strip():
            continue

        emb = model.encode(text).tolist()
        new_data.append({
            "id": item_id,
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

    cvungvien_embeddings = embed_data(ungvien_list, 'CvUngVien_Collection', format_cvungvien_json)
    congviec_embeddings = embed_data(congviec_list, 'CongViec_Collection', format_congviec_json)

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
    role = request.args.get("role", "")
    history_commu = request.args.get("history_communication", "")
 
    if not question.strip():
        return jsonify({"error": "Missing question"}), 400

    prompt = f"""Tôi muốn bạn rút ra các từ khoá đại diện cho: Lĩnh vực công việc, tên công việc, kỹ năng làm việc, phúc lợi việc làm, địa điểm làm việc, thời gian làm việc, mức lương, trình độ học vấn, kinh nghiệm làm việc của 1 công việc.
                Chỉ cần liệt kê các thông tin tôi cần(Lĩnh vực công việc, tên công việc ,kỹ năng làm việc, phúc lợi việc làm, địa điểm làm việc, thời gian làm việc, mức lương, trình độ học vấn, kinh nghiệm làm việc). Gói các thông tin vừa liệt kê thành JSON.***Chỉ cần JSON. Hãy lượt bỏ các thông tin dư thừa khác***
                Nếu không có thông tin cho mục trên thì bỏ qua mục đó, không cần nhắc đến những thông tin khác.
                Giờ thì làm theo hướng dẫn đó của tôi, bạn hãy lọc các từ khoá quan trọng trong câu sau:{question}"""
    print(prompt)
    question_AI = call_ollama_model(prompt)
    print(question_AI)
    # Mã hóa câu hỏi
    try:
        question_emb = model.encode(question_AI).tolist()
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
                n_results=15,
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

    # Gom nhóm kết quả theo collection
    grouped = {
        "CongViec_Collection": [],
        "CvUngVien_Collection": []
    }
    for item in results:
        if item["collection"] in grouped:
            grouped[item["collection"]].append(item["document"])
    # Format context rõ ràng
    context_parts = {
        "CongViec_Collection": "\n".join(f"- {doc}" for doc in grouped["CongViec_Collection"]) or "- Không có dữ liệu phù hợp",
        "CvUngVien_Collection": "\n".join(f"- {doc}" for doc in grouped["CvUngVien_Collection"]) or "- Không có dữ liệu phù hợp"
    }
    # Prompt tối ưu, hướng dẫn LLM trả lời chính xác
    
    prompt = ""
    prompt = f"""
        📌 Bạn là một trợ lý ảo thân thiện của trang website tuyển dụng JobOne, tên là JobOneAgent, chuyên hỗ trợ người dùng trong hệ thống tuyển dụng trực tuyến.

        🎯 **QUY TẮC BẮT BUỘC – PHẢI TUÂN THỦ 100%:**

             1. **TUYỆT ĐỐI TÔN TRỌNG DỮ LIỆU HỆ THỐNG. KHÔNG ĐƯỢC SUY DIỄN, BỔ SUNG, HAY THAY ĐỔI DỮ LIỆU.**
                - Nếu dữ liệu không đủ hoặc không tìm thấy phù hợp, hãy trả lời: **"Hiện tại, tôi chưa có thông tin phù hợp trong hệ thống."**
                - Không được sử dụng kiến thức từ các nguồn khác hoặc dữ liệu huấn luyện.
                - Không hiển thị các giá trị rỗng hoặc `"None"` và không hiển thị các trường kỹ thuật như `ID`, `internal code`, v.v.

             2. **Ưu tiên lọc dữ liệu theo thứ tự sau (nếu có thể):**
                - (1) Địa điểm làm việc
                - (2) Tên công việc / vị trí ứng tuyển, yêu cầu công việc
                - (3) Kinh nghiệm, học vấn, trình độ học vấn, phúc lợi
                - (4) Mức lương và thông tin khác

             3. **Cách trình bày danh sách:**
                - Nếu là **danh sách công việc**, mỗi dòng sẽ chứa các thông tin sau:
                  👉 `TenCongViec - TenCongty – DiaDiem – MoTa – MucLuong – CachThucUngTuyen - YeuCauKinhNghiem - HanNop`
                - Nếu là **danh sách CV ứng viên**, mỗi dòng sẽ chứa các thông tin sau:
                  👉 `HoTen – ViTriUngTuyen1 – TrinhDoHocVan – KinhNghiemLamViec`
                - Tối đa 5 dòng, sau đó nói:  
                  👉 **"Còn nhiều kết quả khác trong hệ thống..."**

             4**Cách phản hồi:**
                - Trả lời hoàn toàn bằng **tiếng VIỆT** có dấu câu (TenCongty, TenCongViec thì giữ nguyên như trong dữ liệu hệ thống).
                - Ngôn ngữ thân thiện, lịch sự, ngắn gọn, đúng trọng tâm, NGHIÊM TÚC, KHÔNG ĐÙA GIỠN, TUÂN THỦ TOÀN BỘ CÁC QUY TẮC.
                - Không lặp lại ý nghĩa trong câu trả lời, không tự nếu các nguyên tắc phản hồi trong phần trả lời.
                - Không được nhắc đến các trang website hoặc ứng dụng tuyển dụng việc làm khác.
                - Nếu là ứng viên thì chỉ trả lời liên quan đến công việc đang tuyển dụng, thông tin công ty đang tuyển dụng.
                - Nếu là nhà tuyển dụng thì chỉ trả lời liên quan đến CV của ứng viên.
                - Nếu là chào hỏi, hỏi thăm: Trả lời thân thiện, tự nhiên, mang tính cá nhân. Không cần liệt kê dữ liệu hệ thống.

         --- 

        🧾 **DỮ LIỆU HỆ THỐNG (DẠNG JSON)**

             ### 🧠 DANH SÁCH CÔNG VIỆC TRONG HỆ THỐNG (Dùng khi người hỏi là ứng viên): 
             {context_parts["CongViec_Collection"]}

             ### 👤 DANH SÁCH CV CỦA ỨNG VIÊN TRONG HỆ THỐNG (Dùng khi người hỏi là nhà tuyển dụng, nếu là ứng viên thì không cần xem dữ liệu này):
             {context_parts["CvUngVien_Collection"]}

         **LƯU Ý QUAN TRỌNG:** Nếu không có dữ liệu nào phù hợp, hoặc nếu thông tin không đủ để trả lời, bạn phải nói rõ: **"Hiện tại, hệ thống chưa có thông tin phù hợp với yêu cầu của bạn."**

         ❓ **Câu hỏi người dùng:** Tôi là {role}. Dựa vào dữ liệu hệ thống dạng JSON trả lời câu hỏi: {question}.
    """.strip()

    print(prompt)
    
    answer = call_ollama_model(prompt)
    
    if answer is None:
        return jsonify({"error": f"Lỗi khi gọi Ollama API: {error}"}), 500
    
    return jsonify({
        "answer": answer
    })

def call_ollama_model(prompt):
    try:
        response = session.post("http://localhost:11434/api/generate", json={
            "model": "openhermes",
            "prompt": prompt,
            "stream": False
        }, timeout=120)
        
        response.raise_for_status()  # phát hiện lỗi HTTP sớm
        answer = response.json().get("response", "Không có phản hồi từ mô hình.")
        return answer
    except requests.exceptions.Timeout:
        return "⏰ Quá thời gian đợi phản hồi."
    except requests.exceptions.RequestException as e:
        return f"Lỗi khi gọi Ollama API: {str(e)}"



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
