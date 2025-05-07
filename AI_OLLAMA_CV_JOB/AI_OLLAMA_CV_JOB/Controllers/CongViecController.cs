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
        /* public async Task<IActionResult> GetData_prepareChroma()
         {
             try
             {
                 var CongViecs = (await congViecRepository.GetTatCaCongViec())?.ToList() ?? new List<CongViec>();
                 var CvUngViens = (await cvUngVienRepository.GetTatCaCV())?.ToList() ?? new List<CvUngVien>();
                 var ViTriLamViecs = (await viTriLamViecRepository.GetTatCa())?.ToList() ?? new List<ViTriLamViec>();

                 var dataToPY = new DataToPY
                 {
                     CongViecs = CongViecs,
                     CvUngViens = CvUngViens,
                     ViTriLamViecs = ViTriLamViecs
                 };

                 using (var client = new HttpClient())
                 {
                     var json = JsonConvert.SerializeObject(dataToPY);
                     var content = new StringContent(json, Encoding.UTF8, "application/json");

                     var response = await client.PostAsync("http://localhost:5000/process-data", content);
                     var result = await response.Content.ReadAsStringAsync();

                     if (!response.IsSuccessStatusCode)
                         return StatusCode((int)response.StatusCode, result);

                     var responseData = JsonConvert.DeserializeObject<object>(result);
                     return Ok(responseData);
                 }
             }
             catch (Exception ex)
             {
                 return StatusCode(500, new { message = "Internal Server Error", error = ex.Message });
             }
         }*/
      
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


        /*public async Task GetData_prepareChroma()
        {
            try
            {
                var CongViecs = (await congViecRepository.GetTatCaCongViec())?.ToList() ?? new List<CongViec>();
                var CvUngViens = (await cvUngVienRepository.GetTatCaCV())?.ToList() ?? new List<CvUngVien>();
                var ViTriLamViecs = (await viTriLamViecRepository.GetTatCa())?.ToList() ?? new List<ViTriLamViec>();

                var dataToPY = new
                {
                    CongViecs,
                    CvUngViens,
                    ViTriLamViecs
                };

                var json = JsonConvert.SerializeObject(dataToPY);

                var psi = new ProcessStartInfo
                {
                    FileName = "python3", // hoặc "python" tùy hệ điều hành
                    Arguments = "script_chroma.py",
                    RedirectStandardInput = true,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    UseShellExecute = false,
                    CreateNoWindow = true
                };

                using (var process = new Process())
                {
                    process.StartInfo = psi;
                    process.Start();

                    // Gửi JSON vào stdin của Python
                    await process.StandardInput.WriteAsync(json);
                    process.StandardInput.Close();

                    // Đọc kết quả in từ stdout
                    string output = await process.StandardOutput.ReadToEndAsync();
                    string errors = await process.StandardError.ReadToEndAsync();
                    process.WaitForExit();

                    Console.WriteLine("Output from Python:\n" + output);
                    if (!string.IsNullOrWhiteSpace(errors))
                        Console.WriteLine("Error:\n" + errors);
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"❌ Lỗi: {ex.Message}");
            }
        }*/
        /* public IActionResult Index()
         {
             var psi = new ProcessStartInfo();
             psi.FileName = "python";
             psi.Arguments = "Scripts/embedding_script.py";
             psi.RedirectStandardOutput = true;
             psi.RedirectStandardError = true;
             psi.UseShellExecute = false;

             var process = Process.Start(psi);
             process.WaitForExit();

             string output = process.StandardOutput.ReadToEnd();
             string error = process.StandardError.ReadToEnd();

             ViewBag.Output = output;
             ViewBag.Error = error;

             // Đọc file saved_data.txt nếu có
             string savedDataPath = "saved_data.txt";
             if (System.IO.File.Exists(savedDataPath))
             {
                 string savedData = System.IO.File.ReadAllText(savedDataPath);
                 ViewBag.SavedData = savedData;
             }
             else
             {
                 ViewBag.SavedData = "Không tìm thấy file saved_data.txt.";
             }

             return View();
         }*/
    }
}
