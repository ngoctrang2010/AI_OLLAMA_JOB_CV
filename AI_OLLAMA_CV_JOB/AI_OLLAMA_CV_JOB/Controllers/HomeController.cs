using AI_OLLAMA_CV_JOB.Models;
using AI_OLLAMA_CV_JOB.Repository;
using DocumentFormat.OpenXml.Packaging;
using Microsoft.AspNetCore.Mvc;
using System.Diagnostics;
using System.Text;
using UglyToad.PdfPig;
using System.Net.Http.Json;
using System.Globalization;

namespace AI_OLLAMA_CV_JOB.Controllers
{
    public class HomeController : Controller
    {
        private readonly ILogger<HomeController> _logger;
        private readonly CongViecRepository congViecRepository;
        private readonly NhaTuyenDungRepository nhaTuyenDungRepository;
        private readonly UngVienRepository ungVienRepository;

        public HomeController(ILogger<HomeController> logger,
            NhaTuyenDungRepository nhaTuyenDungRepository,
            UngVienRepository ungVienRepository,
            CongViecRepository congViecRepository)
        {
            _logger = logger;
            this.nhaTuyenDungRepository = nhaTuyenDungRepository;
            this.ungVienRepository = ungVienRepository;
            this.congViecRepository = congViecRepository;
        }

        public async Task<IActionResult> Index()
        {
            var CongViecs = await congViecRepository.GetTatCaCongViec();
            return View(CongViecs);
        }

        public async Task<IActionResult> DetailJob(int id)
        {
            var CongViec = await congViecRepository.GetCongViecTheoId(id);
            return View(CongViec);
        }

        public IActionResult Privacy()
        {
            return View();
        }

        [ResponseCache(Duration = 0, Location = ResponseCacheLocation.None, NoStore = true)]
        public IActionResult Error()
        {
            return View(new ErrorViewModel { RequestId = Activity.Current?.Id ?? HttpContext.TraceIdentifier });
        }

        // ------------------ TRÍCH XUẤT FILE ------------------
        public static string ExtractText(IFormFile file)
        {
            if (file.FileName.EndsWith(".pdf"))
            {
                using var stream = file.OpenReadStream();
                using var pdf = PdfDocument.Open(stream);
                var sb = new StringBuilder();
                foreach (var page in pdf.GetPages())
                {
                    sb.AppendLine(page.Text);
                }
                return sb.ToString();
            }
            else if (file.FileName.EndsWith(".docx"))
            {
                using var memoryStream = new MemoryStream();
                file.CopyTo(memoryStream);
                memoryStream.Position = 0;

                using var wordDoc = WordprocessingDocument.Open(memoryStream, false);
                return wordDoc.MainDocumentPart.Document.Body.InnerText;
            }

            return string.Empty;
        }

        public static string ExtractTextFromFilePath(string filePath)
        {
            if (filePath.EndsWith(".pdf"))
            {
                using var stream = System.IO.File.OpenRead(filePath);
                using var pdf = PdfDocument.Open(stream);
                var sb = new StringBuilder();
                foreach (var page in pdf.GetPages())
                {
                    sb.AppendLine(page.Text);
                }
                return sb.ToString();
            }
            else if (filePath.EndsWith(".docx"))
            {
                using var stream = System.IO.File.OpenRead(filePath);
                using var wordDoc = WordprocessingDocument.Open(stream, false);
                return wordDoc.MainDocumentPart.Document.Body.InnerText;
            }

            return string.Empty;
        }

        // ------------------ GỌI API AI ------------------
        public class AIResponse
        {
            public string response { get; set; }
        }

        public async Task<string> GoiYJobBangAI(string cvText, List<CongViec> jobs)
        {
            using var client = new HttpClient();
            var url = "http://localhost:11434/api/generate"; // URL OLLAMA hoặc API khác của bạn

            string prompt = $@"
                Dựa trên nội dung CV sau đây, hãy đề xuất 3 công việc phù hợp nhất cho ứng viên từ danh sách công việc bên dưới.
                CV:
                {cvText}

                Danh sách công việc:
                {string.Join("\n", jobs.Select(j => j.TenCongViec))}

                Hãy trả lời bằng tiếng Việt, kèm giải thích lý do chọn từng công việc.
                ";

            var body = new
            {
                model = "llama3", // tên model bạn đang dùng
                prompt = prompt,
                stream = false
            };

            var response = await client.PostAsJsonAsync(url, body);
            var result = await response.Content.ReadFromJsonAsync<AIResponse>();
            return result?.response ?? "Không thể phân tích CV.";
        }

        // ------------------ PHÂN TÍCH CV ------------------
        public async Task<IActionResult> PhanTichCV(string fileName)
        {
            var filePath = Path.Combine(Directory.GetCurrentDirectory(), "wwwroot", "CVs", fileName);
            if (!System.IO.File.Exists(filePath))
            {
                return NotFound("Không tìm thấy file CV.");
            }

            string cvText = ExtractTextFromFilePath(filePath);
            var jobs = await congViecRepository.GetTatCaCongViec();
            if (jobs == null || !jobs.Any())
            {
                ViewBag.Suggestions = "Không có công việc nào trong hệ thống để phân tích.";
            }
            else
            {
                string aiResult = await GoiYJobBangAI(cvText, jobs.ToList());
                ViewBag.Suggestions = aiResult;
            }

            return View();
        }

        [HttpGet]
        public IActionResult Login()
        {
            return View();
        }

        [HttpPost]
        public async Task<IActionResult> Login(string sdt, string email)
        {

            var ungVien = await ungVienRepository.Login(sdt, email);
            if (ungVien == null)
            {
                ViewBag.Message = "Số điện thoại hoặc email không đúng.";
                return View(sdt, email);
            }

            // Đăng nhập thành công => lưu session
            HttpContext.Session.SetInt32("UngVienId", ungVien.Id);
            HttpContext.Session.SetString("UngVienHoTen", ungVien.HoTen ?? "Ứng viên");

            return RedirectToAction("Index", "Home");
        }

        public IActionResult Logout()
        {
            HttpContext.Session.Clear();
            return RedirectToAction("Index", "Home");
        }

        public IActionResult ChatAI()
        {
            var ungVienId = HttpContext.Session.GetInt32("UngVienId");

            if (ungVienId == null)
            {
                return RedirectToAction("Login", "Home");
            }

            return RedirectToAction("ChatBox", "Home");
        }
        public IActionResult ChatBox()
        {
            // Sau này bạn có thể hiển thị giao diện chat tại đây
            return View();
        }
    }
}
