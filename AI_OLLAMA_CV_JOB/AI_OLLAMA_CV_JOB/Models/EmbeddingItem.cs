using Newtonsoft.Json;

namespace AI_OLLAMA_CV_JOB.Models
{
    public class EmbeddingItem
    {
        [JsonProperty("id")]
        public string Id { get; set; }

        [JsonProperty("document")]
        public string Document { get; set; }

        [JsonProperty("embedding")]
        public List<float> Embedding { get; set; }
    }

}
