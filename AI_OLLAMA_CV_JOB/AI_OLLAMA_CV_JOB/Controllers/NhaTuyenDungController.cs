using Microsoft.AspNetCore.Mvc;
using AI_OLLAMA_CV_JOB.Models;
using System.IO;
using System.Linq;
using Microsoft.AspNetCore.Http;
using DocumentFormat.OpenXml.Packaging;
using System.IO;
using iTextSharp.text.pdf;
using iTextSharp.text.pdf.parser;
using DocumentFormat.OpenXml.Packaging;
using Microsoft.EntityFrameworkCore;
using Microsoft.Office.Interop.Word;
using System.Text;
using Newtonsoft.Json;
namespace AI_OLLAMA_CV_JOB.Controllers
{
    public class NhaTuyenDungController : Controller
    {
        private readonly AiOllamaCvJobContext _context;

        public NhaTuyenDungController(AiOllamaCvJobContext context)
        {
            _context = context;
        }

        public IActionResult Index()
        {
            var nhaTuyenDungs = _context.NhaTuyenDungs.ToList();
            return View(nhaTuyenDungs);
        }

        public IActionResult Details(int id)
        {
            var nhaTuyenDung = _context.NhaTuyenDungs.FirstOrDefault(ntd => ntd.Id == id);
            if (nhaTuyenDung == null)
            {
                return NotFound();
            }
            return View(nhaTuyenDung);
        }

        public IActionResult Create()
        {
            return View();
        }

        [HttpPost]
        public IActionResult Create(NhaTuyenDung nhaTuyenDung)
        {
            if (ModelState.IsValid)
            {
                _context.NhaTuyenDungs.Add(nhaTuyenDung);
                _context.SaveChanges();
                return RedirectToAction(nameof(Index));
            }
            return View(nhaTuyenDung);
        }


        [HttpPost]
        public async Task<IActionResult> UploadFile(IFormFile file, int companyId)
        {
            if (file != null && file.Length > 0 && companyId > 0)
            {
                var uploadsFolder = System.IO.Path.Combine(Directory.GetCurrentDirectory(), "wwwroot/uploads");

                if (!Directory.Exists(uploadsFolder))
                {
                    Directory.CreateDirectory(uploadsFolder);
                }

                var nhaTuyenDung = _context.NhaTuyenDungs.FirstOrDefault(ntd => ntd.Id == companyId);
                if (nhaTuyenDung == null)
                {
                    TempData["Error"] = "Nhà tuyển dụng không tồn tại!";
                    return RedirectToAction(nameof(Index));
                }

                var companyName = nhaTuyenDung.TenCongty?.Replace(" ", "_").Replace("/", "").Replace("\\", "");
                var fileExtension = System.IO.Path.GetExtension(file.FileName);

                var fileName = $"{companyName}_{DateTime.Now:yyyyMMddHHmmss}{fileExtension}";
                var filePath = System.IO.Path.Combine(uploadsFolder, fileName);
                var urlPath = "/uploads/" + fileName;

                using (var stream = new FileStream(filePath, FileMode.Create, FileAccess.Write, FileShare.None))
                {
                    file.CopyTo(stream);
                }

                // **Xử lý đọc nội dung file**
                string fileContent = "";
                if (fileExtension == ".pdf")
                {
                    fileContent = ReadPdfContent(file.OpenReadStream());
                }
                else if (fileExtension == ".docx")
                {
                    fileContent = ReadWordContent(file.OpenReadStream());
                }
                else if (fileExtension == ".doc")
                {
                    fileContent = ReadDocContent(filePath);
                }
                else
                {
                    using (var reader = new StreamReader(file.OpenReadStream()))
                    {
                        fileContent = reader.ReadToEnd();
                    }
                }

                // Gọi API gửi vector (và chờ kết quả)
                await SendToVectorDB(companyId.ToString(), nhaTuyenDung.TenCongty, fileContent);

                // **Lưu đường dẫn file vào bảng `NhaTuyenDung`**
                nhaTuyenDung.DuongDanTep = urlPath;
                _context.SaveChanges();

                // **Kiểm tra nếu nội quy đã tồn tại, thì cập nhật nội dung**
                var noiQuyCty = _context.NoiQuyCties.FirstOrDefault(nqc => nqc.IdCty == companyId);
                if (noiQuyCty != null)
                {
                    noiQuyCty.Noidung = fileContent;
                }
                else
                {
                    noiQuyCty = new NoiQuyCty
                    {
                        IdCty = companyId,
                        Noidung = fileContent
                    };
                    _context.NoiQuyCties.Add(noiQuyCty);
                }

                _context.SaveChanges();

                TempData["Success"] = "File đã được tải lên, nội dung cũ đã được thay thế!";
                return RedirectToAction(nameof(Index));
            }

            TempData["Error"] = "Vui lòng chọn công ty và file hợp lệ.";
            return RedirectToAction(nameof(Index));
        }

        // Đọc nội dung file PDF
        public string ReadPdfContent(Stream pdfStream)
        {
            using (var reader = new PdfReader(pdfStream))
            {
                StringBuilder text = new StringBuilder();
                for (int i = 1; i <= reader.NumberOfPages; i++)
                {
                    text.Append(PdfTextExtractor.GetTextFromPage(reader, i));
                }
                return text.ToString();
            }
        }

        // Đọc nội dung file Word (.docx)
        public string ReadWordContent(Stream wordStream)
        {
            using (WordprocessingDocument wordDoc = WordprocessingDocument.Open(wordStream, false))
            {
                var body = wordDoc.MainDocumentPart.Document.Body;
                return body.InnerText;
            }
        }
        public string ReadDocContent(string filePath)
        {
            Application wordApp = new Application();
            Document doc = wordApp.Documents.Open(filePath);

            string text = doc.Content.Text;

            // Đóng tài liệu sau khi đọc
            doc.Close(false);
            wordApp.Quit();

            return text;
        }
        public async Task<bool> SendToVectorDB(string docId, string companyName, string content)
        {
            var httpClient = new HttpClient();
            var url = "http://127.0.0.1:8000/vectorize/";

            var payload = new
            {
                doc_id = docId,
                company_name = companyName,  // Gửi tên công ty
                content = content
            };

            var jsonContent = new StringContent(JsonConvert.SerializeObject(payload), Encoding.UTF8, "application/json");

            var response = await httpClient.PostAsync(url, jsonContent);
            return response.IsSuccessStatusCode;
        }

    }
}
