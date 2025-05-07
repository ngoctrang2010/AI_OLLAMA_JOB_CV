using AI_OLLAMA_CV_JOB.Models;
using AI_OLLAMA_CV_JOB.Repository;
using Microsoft.AspNetCore.Mvc;
using System.Diagnostics;
using Newtonsoft.Json;
using System.Text;


namespace AI_OLLAMA_CV_JOB.Controllers
{
    public class CongViecController : Controller
    {
        private readonly CongViecRepository congViecRepository;
        private readonly NhaTuyenDungRepository nhaTuyenDungRepository;
        private readonly UngVienRepository ungVienRepository;
        private readonly ViTriLamViecRepository viTriLamViecRepository;
        private readonly CvUngVienRepository cvUngVienRepository;

        public CongViecController(
            NhaTuyenDungRepository nhaTuyenDungRepository,
            UngVienRepository ungVienRepository,
            CongViecRepository congViecRepository,
            ViTriLamViecRepository viTriLamViecRepository,
            CvUngVienRepository cvUngVienRepository)
        {
            this.nhaTuyenDungRepository = nhaTuyenDungRepository;
            this.ungVienRepository = ungVienRepository;
            this.congViecRepository = congViecRepository;
            this.cvUngVienRepository = cvUngVienRepository;
            this.viTriLamViecRepository = viTriLamViecRepository;
        }
        public class DataToPY
        {
            public List<CongViec> CongViecs { get; set; } = new List<CongViec>();
            public List<ViTriLamViec> ViTriLamViecs { get; set; } = new List<ViTriLamViec>();
            public List<CvUngVien> CvUngViens { get; set; } = new List<CvUngVien>();
        }
      
        public class ResponseData
        {
            [JsonProperty("congviec_embeddings")]
            public List<EmbeddingItem> CongViecEmbeddings { get; set; }

            [JsonProperty("cvungvien_embeddings")]
            public List<EmbeddingItem> CvUngVienEmbeddings { get; set; }

            [JsonProperty("vitri_embeddings")]
            public List<EmbeddingItem> ViTriEmbeddings { get; set; }
        }

        public async Task<IActionResult> GetData_prepareChroma()
        {
            try
            {
                var CongViecs = (await congViecRepository.GetTatCaCongViec())?.ToList() ?? new List<CongViec>();
                var CvUngViens = (await cvUngVienRepository.GetTatCaCV())?.ToList() ?? new List<CvUngVien>();
                var ViTriLamViecs = (await viTriLamViecRepository.GetTatCa())?.ToList() ?? new List<ViTriLamViec>();

                var dataToPY = new
                {
                    CongViecs = CongViecs.Select(cv => new
                    {
                        cv.Id,
                        cv.IdNtd,
                        cv.TenCongViec,
                        cv.MoTaCongViec,
                        cv.YeuCauCongViec,
                        cv.PhucLoi,
                        cv.DiaDiemThoiGian,
                        cv.CachThucUngTuyen,
                        cv.KinhNghiem,
                        cv.MucLuong,
                        cv.HanNop,
                        cv.HocVan
                    }).ToList(),
                    CvUngViens = CvUngViens.Select(cvu => new
                    {
                        cvu.Id,
                        cvu.ViTriUngTuyen,
                        cvu.HocVan,
                        cvu.KinhNghiem,
                        cvu.DuAn,
                        cvu.ChungChi,
                        cvu.IdUngVien
                    }).ToList(),
                    ViTriLamViecs = ViTriLamViecs.Select(vtlv => new
                    {
                        vtlv.Id,
                        vtlv.IdUngVien,
                        vtlv.ViTriTuyenDung,
                        vtlv.LamViecTai,
                        vtlv.HinhThucLamViec,
                        vtlv.TrinhDo,
                        vtlv.MucLuong,
                        vtlv.HocVan
                    }).ToList()
                };

                using (var client = new HttpClient())
                {
                    var json = JsonConvert.SerializeObject(dataToPY);
                    var content = new StringContent(json, Encoding.UTF8, "application/json");

                    var response = await client.PostAsync("http://localhost:5000/process-data", content);
                    var result = await response.Content.ReadAsStringAsync();

                    if (!response.IsSuccessStatusCode)
                    {
                        return StatusCode((int)response.StatusCode, result);
                    }

                    var responseData = JsonConvert.DeserializeObject<ResponseData>(result);

                    ViewData["congviec_embeddings"] = responseData.CongViecEmbeddings;
                    ViewData["cvungvien_embeddings"] = responseData.CvUngVienEmbeddings;
                    ViewData["vitri_embeddings"] = responseData.ViTriEmbeddings;

                    return View(); // Trả về một View hiển thị dữ liệu nếu cần
                }
            }
            catch (Exception ex)
            {
                return StatusCode(500, new { message = "Internal Server Error", error = ex.Message });
            }
        }
        public IActionResult Index()
        {
            var psi = new ProcessStartInfo
            {
                FileName = "python",
                Arguments = "Scripts/embedding_script.py",
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false,
                CreateNoWindow = true
            };

            string output = "";
            string error = "";

            try
            {
                using (var process = Process.Start(psi))
                {
                    if (process != null)
                    {
                        output = process.StandardOutput.ReadToEnd();
                        error = process.StandardError.ReadToEnd();
                        process.WaitForExit();
                    }
                    else
                    {
                        error = "Không thể khởi động process Python.";
                    }
                }
            }
            catch (Exception ex)
            {
                error = $"Lỗi khi chạy script: {ex.Message}";
            }

            ViewBag.Output = output;
            ViewBag.Error = error;

            // Đọc file saved_vectors.txt (chứa hết 3 bảng)
            string savedDataPath = Path.Combine(Directory.GetCurrentDirectory(), "saved_vectors_with_ids.txt");
            string savedData;
            if (System.IO.File.Exists(savedDataPath))
            {
                savedData = System.IO.File.ReadAllText(savedDataPath);
            }
            else
            {
                savedData = "Không tìm thấy file saved_vectors.txt.";
            }

            ViewBag.SavedData = savedData;

            return View();
        }
    }
}
