using System;
using System.ComponentModel.DataAnnotations;

namespace web_app.Models
{
    public class PredictionRecord
    {
        public int Id { get; set; }

        [Required]
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

        [Required]
        public string FeaturesJson { get; set; } = "";

        public double Prediction { get; set; }
    }
}
