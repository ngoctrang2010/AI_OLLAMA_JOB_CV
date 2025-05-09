using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using Newtonsoft.Json;
using System;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using AI_OLLAMA_CV_JOB.Models;

public class ChatController : Controller
{
    private readonly ILogger<ChatController> _logger;
    private readonly IHttpClientFactory _httpClientFactory;

    public ChatController(ILogger<ChatController> logger, IHttpClientFactory httpClientFactory)
    {
        _logger = logger;
        _httpClientFactory = httpClientFactory;
    }

    public ActionResult Index()
    {
        return View(new ChatModel());
    }

    [HttpPost]
    public async Task<ActionResult> Ask(ChatModel model)
    {
        if (string.IsNullOrEmpty(model.Question))
        {
            ModelState.AddModelError("", "Vui lòng nhập câu hỏi.");
            return View("Index", model);
        }

        var answer = await CallFastApiForText(model.Question);
        model.Answer = answer;

        return View("Index", model);
    }

    [HttpPost]
    public async Task<ActionResult> Upload(IFormFile file)
    {
        if (file == null || file.Length == 0)
        {
            ModelState.AddModelError("", "Vui lòng chọn file PDF.");
            return View("Index", new ChatModel());
        }

        var answer = await CallFastApiForFile(file);
        var model = new ChatModel
        {
            Answer = answer
        };

        return View("Index", model);
    }

    private async Task<string> CallFastApiForText(string prompt)
    {
        var client = _httpClientFactory.CreateClient();
        client.Timeout = TimeSpan.FromMinutes(4);

        var url = "http://localhost:8000/ask_question/";
        var payload = new
        {
            question_text = prompt,
            model_name = "tinyllama",
            top_k = 5
        };

        var content = new StringContent(JsonConvert.SerializeObject(payload), Encoding.UTF8, "application/json");

        try
        {
            var response = await client.PostAsync(url, content);
            var responseData = await response.Content.ReadAsStringAsync();

            if (!response.IsSuccessStatusCode)
            {
                _logger.LogError("FastAPI trả về lỗi {StatusCode}: {Content}", response.StatusCode, responseData);
                return $"Lỗi từ FastAPI: {response.StatusCode} - {responseData}";
            }

            var data = JsonConvert.DeserializeObject<FastApiResponse>(responseData);
            return data?.answer ?? "Không nhận được trả lời từ FastAPI.";
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Lỗi khi gọi FastAPI.");
            return $"Có lỗi xảy ra khi gọi API: {ex.Message}";
        }
    }

    private async Task<string> CallFastApiForFile(IFormFile file)
    {
        var client = _httpClientFactory.CreateClient();
        client.Timeout = TimeSpan.FromMinutes(4);

        var url = "http://localhost:8000/extract_text/";

        using var content = new MultipartFormDataContent();
        using var stream = file.OpenReadStream();
        using var fileContent = new StreamContent(stream);

        fileContent.Headers.ContentType = new System.Net.Http.Headers.MediaTypeHeaderValue(file.ContentType);
        content.Add(fileContent, "file", file.FileName);

        try
        {
            var response = await client.PostAsync(url, content);
            var responseData = await response.Content.ReadAsStringAsync();

            if (!response.IsSuccessStatusCode)
            {
                _logger.LogError("FastAPI trả về lỗi {StatusCode}: {Content}", response.StatusCode, responseData);
                return $"Lỗi từ FastAPI ({response.StatusCode}): {responseData}";
            }

            var data = JsonConvert.DeserializeObject<FastApiResponse>(responseData);
            return data?.answer ?? "Không nhận được trả lời từ FastAPI.";
        }
        catch (TaskCanceledException ex)
        {
            _logger.LogError(ex, "API FastAPI mất quá nhiều thời gian để phản hồi.");
            return "FastAPI phản hồi quá lâu, vui lòng thử lại sau.";
        }
        catch (HttpRequestException ex)
        {
            _logger.LogError(ex, "Lỗi mạng khi gọi FastAPI.");
            return "Không thể kết nối đến FastAPI, kiểm tra lại máy chủ.";
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Lỗi không xác định khi gọi FastAPI.");
            return $"Có lỗi xảy ra khi gọi API: {ex.Message}";
        }
    }


    public class FastApiResponse
    {
        public string answer { get; set; }
    }
}
