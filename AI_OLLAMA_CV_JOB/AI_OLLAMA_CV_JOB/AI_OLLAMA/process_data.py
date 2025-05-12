
from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer
from chromadb import PersistentClient
import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import requests
from concurrent.futures import ThreadPoolExecutor
from flask_cors import CORS
from pydantic import BaseModel, ValidationError

app = Flask(__name__)
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
os.environ["CHROMA_DB_PATH"] = "./wwwroot/Chroma_data/chroma.sqlite" 
CORS(app)
client = PersistentClient(
    path="./wwwroot/Chroma_data"
)
collection = client.get_or_create_collection(name="document_vectors")
# Mô hình dữ liệu nội quy
class DocumentData(BaseModel):
    doc_id: str
    company_name: str
    content: str
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
def format_company_rule(data):
    return (
        f"🔹 ID: {data.get('Id', '')}\n"
        f"🔹 Tên công ty: {data.get('CompanyName', '')}\n"
        f"🔹 Nội quy: {data.get('Content', '')}"
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

        📌 **Yêu cầu phản hồi bằng tiếng Việt. Tên công ty hoặc công việc giữ nguyên (không dịch). Trả lời ngắn gọn, rõ ràng và đúng mục tiêu. Loại bỏ các ID đi.**
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



@app.route('/vectorize/', methods=['POST'])
def vectorize_document():
    try:
        # Nhận JSON data từ request
        json_data = request.get_json()
        if not json_data:
            return jsonify({"error": "No JSON data provided"}), 400

        # Validate dữ liệu đầu vào bằng Pydantic
        try:
            data = DocumentData(**json_data)
        except ValidationError as e:
            return jsonify({"error": e.errors()}), 400

        # Kiểm tra collection trước khi thao tác
        try:
            collection = client.get_collection("company_rules")
        except Exception:
            collection = client.create_collection("company_rules")

        # Kiểm tra xem ID có tồn tại không
        existing_data = collection.get(ids=[data.doc_id])

        if existing_data and 'documents' in existing_data and existing_data['documents']:
            # Nếu tồn tại, xóa dữ liệu cũ trước khi thay thế
            collection.delete(ids=[data.doc_id])

        # Gọi embed_data để format, tạo vector và lưu vào ChromaDB
        embedded_result = embed_data(
            list_data=[{
                "Id": data.doc_id,
                "CompanyName": data.company_name,
                "Content": data.content
            }],
            prefix="company_rules",
            format_func=format_company_rule
        )

        if not embedded_result:
            return jsonify({"error": "Failed to process embedding"}), 500

        return jsonify({
            "message": "Vectorization successful",
            "doc_id": data.doc_id,
            "company": data.company_name,
            "vector_sample": embedded_result[0]["embedding"][:5]  # Hiển thị một phần vector để debug
        }), 200

    except Exception as e:
        import traceback
        print(traceback.format_exc())  # Ghi log lỗi chi tiết
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


@app.route('/vectorize-rule/search/<company_id>', methods=['GET'])
def search_documents(company_id):
    try:
        # Kiểm tra nếu ID không hợp lệ
        if not company_id or not company_id.strip():
            return jsonify({"error": "Company ID is required"}), 400

        # Kiểm tra collection trước khi truy vấn
        try:
            collection = client.get_collection("company_rules")
        except Exception as e:
            return jsonify({"error": f"Collection not found: {str(e)}"}), 500

        # Truy xuất dữ liệu dựa trên company_id
        try:
            results = collection.get(ids=[company_id])
        except Exception as e:
            return jsonify({"error": f"Query failed: {str(e)}"}), 500

        # Kiểm tra kết quả truy vấn
        if not results or not isinstance(results, dict) or 'documents' not in results or not results['documents']:
            return jsonify({"message": "No matching documents found"}, 404)

        # Định dạng kết quả trả về
        document = {
            "doc_id": results['ids'][0],
            "document": results['documents'][0],
            "metadata": results['metadatas'][0]
        }

        return jsonify(document), 200

    except Exception as e:
        import traceback
        print(traceback.format_exc())  # Log lỗi chi tiết
        return jsonify({"error": str(e)}), 500
@app.route('/vectorize-rule/ask-llama/<company_id>', methods=['POST'])
def ask_llama(company_id):
    try:
        # Nhận câu hỏi từ request
        json_data = request.get_json()
        user_question = json_data.get("question", "").strip()

        # Kiểm tra nếu câu hỏi trống
        if not user_question:
            return jsonify({"error": "Question is required"}), 400

        # Lấy nội quy gần nhất từ ChromaDB
        try:
            response = requests.get(f"http://127.0.0.1:5000/vectorize-rule/search/{company_id}")
            response.raise_for_status()  # Kiểm tra nếu request thất bại
            document_data = response.json()
            print("=============== DOCUMENT DATA =================")
            print(document_data)  # In ra dữ liệu từ ChromaDB
            print("===============================================")
        except requests.exceptions.RequestException as e:
            return jsonify({"error": f"Failed to retrieve company rules: {str(e)}"}), 500

        # Kiểm tra dữ liệu từ ChromaDB
        if "document" not in document_data:
            return jsonify({"error": "No matching company rules found"}), 404

        # Tạo prompt cho Llama 3
        prompt = f"""
📌 Bạn là trợ lý ảo **JobOneAgent**, chuyên trả lời câu hỏi dựa vào dữ liệu đã cho.

🎯 **Nguyên tắc trả lời**:
- Trả lời thân thiện, đúng trọng tâm, tránh suy đoán, đúng dữ liệu đã cho.
- Dựa vào thông tin kịch bản mà trả lời, không thêm thông tin ngoài yêu cầu.
- Tránh việc hiển thị bất kỳ thông tin nhạy cảm, bao gồm ID hoặc các thông tin cá nhân.
- Nếu câu hỏi không liên quan đến dữ liệu kịch bản, trả lời lịch sự và giải thích rõ ràng.

📊 **Dữ liệu kịch bản**:
{document_data['metadata']}

❓ **Câu hỏi của người dùng**:
{user_question}

📌 **Yêu cầu phản hồi**:
- Trả lời bằng tiếng Việt, dễ hiểu và chính xác.
- Đảm bảo nội dung trả lời chính xác, phù hợp với câu hỏi, và không thiếu sót.
- Nếu không tìm thấy thông tin liên quan từ kịch bản, hãy trả lời lịch sự, giải thích rõ ràng và gợi ý cách để giải quyết hoặc hỏi lại câu hỏi.
- Tránh thêm thông tin không liên quan đến kịch bản.
""".strip()

        print("====================== PROMPT SENT TO OLLAMA ======================")
        print(prompt)
        print("===================================================================")
            # Gọi API Llama 3
        try:
            llama_response = requests.post("http://localhost:11434/api/generate", json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False
            })
            llama_response.raise_for_status()  # Kiểm tra lỗi HTTP
        except requests.exceptions.RequestException as e:
            return jsonify({"error": f"Failed to call Ollama API: {str(e)}"}), 500

        # Kiểm tra phản hồi từ Llama 3
        llama_data = llama_response.json()
        answer = llama_data.get("response", "Llama 3 không trả về phản hồi.")

        return jsonify({
    "answer": answer,
    "company_rule": {
        "doc_id": document_data.get('doc_id'),
        "document": document_data.get('document'),
        "metadata": document_data.get('metadata')
    }
}), 200

    except Exception as e:
        import traceback
        print(traceback.format_exc())  # Ghi log lỗi chi tiết



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
