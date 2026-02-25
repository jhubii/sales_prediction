using System.Net.Http.Json;
using Microsoft.Extensions.Options;

namespace web_app.Services
{
    public class FastApiOptions
    {
        public string BaseUrl { get; set; } = "";
    }

    public class PredictResponse
    {
        public double prediction { get; set; }
    }

    public class FastApiClient
    {
        private readonly HttpClient _http;

        public FastApiClient(HttpClient http, IOptions<FastApiOptions> opts)
        {
            _http = http;
            _http.BaseAddress = new Uri(opts.Value.BaseUrl);
        }

        public async Task<double> PredictAsync(Dictionary<string, object> features)
        {
            var payload = new { features };
            var res = await _http.PostAsJsonAsync("/predict", payload);
            if (!res.IsSuccessStatusCode)
            {
                var err = await res.Content.ReadAsStringAsync();
                throw new Exception($"FastAPI error: {(int)res.StatusCode} {res.ReasonPhrase}\n{err}");
            }

            var body = await res.Content.ReadFromJsonAsync<PredictResponse>();
            return body?.prediction ?? 0.0;
        }
    }
}
