using Microsoft.EntityFrameworkCore;
using web_app.Models;

namespace web_app.Data
{
    public class AppDbContext : DbContext
    {
        public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }
        public DbSet<PredictionRecord> Predictions => Set<PredictionRecord>();
    }
}
