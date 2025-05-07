using AI_OLLAMA_CV_JOB.Models;
using Microsoft.AspNetCore.Mvc;
using System.Diagnostics;

namespace AI_OLLAMA_CV_JOB.Controllers
{
    public class ChatController : Controller
    {
        private readonly IWebHostEnvironment _env;

        public ChatController(IWebHostEnvironment env)
        {
            _env = env;
        }

        // GET: Chat
        public IActionResult Index()
        {
            var model = new ChatModel();
            return View(model);
        }

        [HttpPost]
        public IActionResult Index(ChatModel model)
        {
            if (!string.IsNullOrEmpty(model.UserQuestion))
            {
                string answer = RunPythonOllama(model.UserQuestion);
                model.OllamaResponse = answer;
            }
            return View(model);
        }

        private string RunPythonOllama(string userQuery)
        {
            // Lấy path tuyệt đối của Python script
            string scriptPath = Path.Combine(_env.ContentRootPath, "Scripts", "ollama_integration.py");

            string pythonExePath = @"C:\Users\ADMIN\AppData\Local\Programs\Python\Python312\python.exe"; // Cập nhật đường dẫn Python đúng máy bạn

            var psi = new ProcessStartInfo
            {
                FileName = pythonExePath,
                Arguments = $"\"{scriptPath}\" \"{userQuery}\"",
                UseShellExecute = false,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                CreateNoWindow = true
            };

            using (var process = Process.Start(psi))
            {
                string output = process.StandardOutput.ReadToEnd();
                string errors = process.StandardError.ReadToEnd();

                process.WaitForExit();

                if (!string.IsNullOrEmpty(errors))
                {
                    return $"Đã xảy ra lỗi: {errors}";
                }

                return output;
            }
        }
    }
}
