import sys
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import ollama

def search_and_respond(query):
    # Kết nối Chroma DB - ĐÚNG CHUẨN MỚI
    client = chromadb.PersistentClient(path="./chroma_data")

    # Kiểm tra collection có tồn tại không
    try:
        collection = client.get_collection("cv_vectors")
    except:
        print("Collection 'cv_vectors' không tồn tại. Vui lòng tạo collection trước.")
        return

    # Load SentenceTransformer
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # Encode câu hỏi
    query_vec = model.encode(query).tolist()

    # Truy vấn 5 CV phù hợp nhất
    results = collection.query(query_embeddings=[query_vec], n_results=5)

    # Xử lý trường hợp không có kết quả
    if not results['documents']:
        print("Không tìm thấy CV phù hợp.")
        return

    # Đảm bảo có đủ 5 kết quả (tránh lỗi index nếu ít hơn)
    docs = results['documents'][0]
    prompt = "Tôi có các CV sau đây:\n"
    for idx, doc in enumerate(docs):
        prompt += f"{idx + 1}. {doc}\n"

    prompt += "\nHãy gợi ý công việc phù hợp cho các ứng viên này theo cách dễ hiểu."

    # Gọi Ollama local
    response = ollama.chat(
        model="llama3",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    # In kết quả để ASP.NET đọc stdout
    print(response['message']['content'])


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Vui lòng nhập câu hỏi tìm kiếm.")
    else:
        query_input = sys.argv[1]
        search_and_respond(query_input)
