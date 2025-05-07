using Microsoft.AspNetCore.Mvc;
using System.Diagnostics;

namespace AI_OLLAMA_CV_JOB.Controllers
{
    public class CongViecController : Controller
    {
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
