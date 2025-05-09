using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;

public class EmbeddingService
{
    private static readonly HttpClient client = new HttpClient();

    public async Task<string> GetEmbeddingAsync(string text)
    {
        var payload = new
        {
            model = "all-MiniLM-L6-v2",  // Model bạn sử dụng
            prompt = text,  // Văn bản cần chuyển thành embedding
            stream = false
        };

        // Serialize the payload to JSON
        var jsonContent = new StringContent(JsonConvert.SerializeObject(payload), Encoding.UTF8, "application/json");

        // Send the POST request to the API
        var response = await client.PostAsync("http://localhost:11434/api/generate", jsonContent);

        if (response.IsSuccessStatusCode)
        {
            var result = await response.Content.ReadAsStringAsync();
            return result;  // Trả về kết quả từ API
        }
        else
        {
            return $"Error: {response.StatusCode}";  // Trả về lỗi nếu API gặp sự cố
        }
    }
}
