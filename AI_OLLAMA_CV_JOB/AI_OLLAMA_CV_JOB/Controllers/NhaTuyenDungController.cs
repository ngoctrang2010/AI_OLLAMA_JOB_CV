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
using System.ComponentModel;
using System.Text.RegularExpressions;
using OfficeOpenXml;
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

                // *Xử lý đọc nội dung file*
                string fileContent = "";
                if (fileExtension == ".pdf")
                {
                    fileContent = ReadPdfContent(file.OpenReadStream());
                }
                else if (fileExtension == ".docx")
                {
                    fileContent = ReadWordContentWithoutPageNumbers(file.OpenReadStream());
                }
                else if (fileExtension == ".doc")
                {
                    fileContent = ReadDocContentWithoutPageNumbers(filePath);
                }
                else if (fileExtension == ".xlsx")
                {
                    fileContent = ReadExcelContent(file.OpenReadStream());
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

                // **Lưu đường dẫn file vào bảng NhaTuyenDung**
                nhaTuyenDung.DuongDanTep = urlPath;
                _context.SaveChanges();

                // *Kiểm tra nếu nội quy đã tồn tại, thì cập nhật nội dung*
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

        public string ReadExcelContent(Stream excelStream)
        {
            // Đặt LicenseContext cho EPPlus
            ExcelPackage.LicenseContext = OfficeOpenXml.LicenseContext.NonCommercial;


            StringBuilder sb = new StringBuilder();

            // Mở gói Excel
            using (var package = new ExcelPackage(excelStream))
            {
                foreach (var worksheet in package.Workbook.Worksheets)
                {
                    sb.AppendLine($"--- Sheet: {worksheet.Name} ---");

                    var rowCount = worksheet.Dimension.Rows;
                    var colCount = worksheet.Dimension.Columns;

                    for (int row = 1; row <= rowCount; row++)
                    {
                        List<string> cells = new List<string>();
                        for (int col = 1; col <= colCount; col++)
                        {
                            var cellValue = worksheet.Cells[row, col].Text;
                            if (!string.IsNullOrWhiteSpace(cellValue))
                                cells.Add(cellValue.Trim());
                        }
                        if (cells.Count > 0)
                            sb.AppendLine(string.Join(" | ", cells));
                    }
                }
            }

            return sb.ToString();
        }

        // Đọc nội dung file PDF

        public string ReadPdfContent(Stream pdfStream)
        {
            StringBuilder text = new StringBuilder();
            using (PdfReader reader = new PdfReader(pdfStream))
            {
                for (int i = 1; i <= reader.NumberOfPages; i++)
                {
                    string pageText = PdfTextExtractor.GetTextFromPage(reader, i);
                    string filtered = FilterText(pageText);
                    text.AppendLine(filtered);
                }
            }
            return text.ToString();
        }

        private string FilterText(string input)
        {
            var lines = input.Split('\n');
            StringBuilder filtered = new StringBuilder();
            foreach (var line in lines)
            {
                string trimmed = line.Trim();

                // Ví dụ loại các dòng:
                // - chỉ số trang: "Page 1", "Page 2 of 10"
                // - copyright: "© CompanyName 2024"
                // - ngày tháng: "Date: 2024-05-10"
                if (string.IsNullOrWhiteSpace(trimmed) ||
                    System.Text.RegularExpressions.Regex.IsMatch(trimmed, @"^Page\s+\d+(\s+of\s+\d+)?$", RegexOptions.IgnoreCase) ||
                    System.Text.RegularExpressions.Regex.IsMatch(trimmed, @"^\d+$") ||
                    trimmed.Contains("CompanyName") ||
                    System.Text.RegularExpressions.Regex.IsMatch(trimmed, @"^Date\s*:\s*\d{4}-\d{2}-\d{2}$", RegexOptions.IgnoreCase)
                    )
                {
                    continue;
                }

                filtered.AppendLine(trimmed);
            }
            return filtered.ToString();
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
        public string ReadWordContentWithoutPageNumbers(Stream wordStream)
        {
            using (WordprocessingDocument wordDoc = WordprocessingDocument.Open(wordStream, false))
            {
                var body = wordDoc.MainDocumentPart.Document.Body;

                // Loại bỏ số trang trong các phần tử của tài liệu
                var pageNumbers = body.Descendants<DocumentFormat.OpenXml.Drawing.Text>().Where(x => x.Text.Contains("Page"));

                foreach (var pageNumber in pageNumbers.ToList())
                {
                    pageNumber.Remove(); // Xóa các phần tử số trang
                }

                return body.InnerText;
            }
        }

        public string ReadDocContentWithoutPageNumbers(string filePath)
        {
            Application wordApp = new Application();
            Document doc = wordApp.Documents.Open(filePath);

            // Loại bỏ số trang
            foreach (Section section in doc.Sections)
            {
                foreach (HeaderFooter headerFooter in section.Headers)
                {
                    if (headerFooter.Exists)
                    {
                        foreach (Paragraph paragraph in headerFooter.Range.Paragraphs)
                        {
                            Microsoft.Office.Interop.Word.Range paraRange = paragraph.Range;
                            if (paraRange.Text.Contains("Page"))
                            {
                                paraRange.Delete(); // Xóa đoạn chứa chữ "Page"
                            }
                        }
                    }
                }



                foreach (HeaderFooter headerFooter in section.Footers)
                {
                    if (headerFooter.Exists)
                    {
                        foreach (Paragraph paragraph in headerFooter.Range.Paragraphs)
                        {
                            Microsoft.Office.Interop.Word.Range paraRange = paragraph.Range;
                            if (paraRange.Text.Contains("Page"))
                            {
                                paraRange.Delete();
                            }
                        }
                    }
                }

            }

            string text = doc.Content.Text;

            // Đóng tài liệu sau khi xử lý
            doc.Close(false);
            wordApp.Quit();

            return text;
        }


        public async Task<bool> SendToVectorDB(string docId, string companyName, string content)
        {
            try
            {
                var httpClient = new HttpClient();
                var url = "http://127.0.0.1:5000/vectorize/";

                var payload = new
                {
                    doc_id = docId,
                    company_name = companyName,  // Gửi tên công ty
                    content = content
                };

                var jsonContent = new StringContent(JsonConvert.SerializeObject(payload), Encoding.UTF8, "application/json");

                var response = await httpClient.PostAsync(url, jsonContent);

                if (response.IsSuccessStatusCode)
                {
                    // Nếu thành công, bạn có thể đọc nội dung phản hồi nếu cần
                    string responseContent = await response.Content.ReadAsStringAsync();
                    // Bạn có thể ghi ra responseContent nếu muốn debug
                    Console.WriteLine(responseContent);
                    return true;
                }
                else
                {
                    // Nếu không thành công, bạn có thể ghi lỗi
                    string errorResponse = await response.Content.ReadAsStringAsync();
                    Console.WriteLine($"Error response: {errorResponse}");
                    return false;
                }
            }
            catch (Exception ex)
            {
                // Nếu có ngoại lệ, bạn có thể xử lý hoặc log lỗi
                Console.WriteLine($"Exception: {ex.Message}");
                return false;
            }

        }

    }
}
