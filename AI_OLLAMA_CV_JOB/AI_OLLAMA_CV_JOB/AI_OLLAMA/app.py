import sys
import json
from sentence_transformers import SentenceTransformer
import chromadb
import os

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
chroma_client = chromadb.PersistentClient(path=os.path.expanduser("~/wwwroot/Chroma_data"))

# Đọc JSON từ stdin
input_data = sys.stdin.read()
data = json.loads(input_data)

def format_congviec(cv):
    return f"""Tên công việc: {cv.get('TenCongViec')}.
    Mô tả: {cv.get('MoTaCongViec')}.
    Yêu cầu: {cv.get('YeuCauCongViec')}.
    Phúc lợi: {cv.get('PhucLoi')}.
    Địa điểm & thời gian: {cv.get('DiaDiemThoiGian')}.
    Cách thức ứng tuyển: {cv.get('CachThucUngTuyen')}.
    Kinh nghiệm: {cv.get('KinhNghiem')} năm.
    Mức lương: {cv.get('MucLuong')}.
    Hạn nộp: {cv.get('HanNop') or 'Không rõ'}.
    Trình độ học vấn: {cv.get('HocVan') or 'Không rõ'}."""

def format_cvungvien(cv):
    return f"""Vị trí ứng tuyển: {cv.get('ViTriUngTuyen')}.
    Học vấn: {cv.get('HocVan')}.
    Kinh nghiệm: {cv.get('KinhNghiem')}.
    Dự án: {cv.get('DuAn') or 'Không có'}.
    Chứng chỉ: {cv.get('ChungChi')}."""

def format_vitri(vt):
    return f"""Vị trí tuyển dụng: {vt.get('ViTriTuyenDung') or 'Không rõ'}.
    Làm việc tại: {vt.get('LamViecTai') or 'Không rõ'}.
    Hình thức làm việc: {vt.get('HinhThucLamViec') or 'Không rõ'}.
    Trình độ yêu cầu: {vt.get('TrinhDo') or 'Không rõ'}.
    Mức lương: {vt.get('MucLuong') or 'Không rõ'}.
    Yêu cầu học vấn: {vt.get('HocVan') or 'Không rõ'}."""

def embed_and_store(list_data, collection_name, prefix, format_func):
    collection = chroma_client.get_or_create_collection(collection_name)
    existing_ids = set(collection.get(include=["ids"])["ids"])

    new_ids, new_docs, new_embeddings = [], [], []

    for item in list_data:
        item_id = f"{prefix}_{item['Id']}"
        if item_id in existing_ids:
            continue

        text = format_func(item)
        if not text.strip():
            continue

        emb = model.encode(text).tolist()
        new_ids.append(item_id)
        new_docs.append(text)
        new_embeddings.append(emb)

    if new_ids:
        collection.add(ids=new_ids, documents=new_docs, embeddings=new_embeddings)
        print(f"✅ Lưu {len(new_ids)} mục mới vào collection '{collection_name}'")
    else:
        print(f"⚠️ Không có mục mới để lưu vào '{collection_name}'")

# Chuyển và lưu từng danh sách
embed_and_store(data.get("CongViecs", []), "congviec_vectors", "CVIEC", format_congviec)
embed_and_store(data.get("CvUngViens", []), "cvungvien_vectors", "UV", format_cvungvien)
embed_and_store(data.get("ViTriLamViecs", []), "vitri_vectors", "VITRI", format_vitri)

print("✅ HOÀN TẤT CHUYỂN ĐỔI VÀ LƯU EMBEDDING.")
