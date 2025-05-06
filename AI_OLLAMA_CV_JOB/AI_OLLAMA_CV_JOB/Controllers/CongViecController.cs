using Microsoft.AspNetCore.Mvc;
using System.Diagnostics;
using System.IO;

namespace AI_OLLAMA_CV_JOB.Controllers
{
    public class CongViecController : Controller
    {
        public IActionResult Index()
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
        }
    }
}
