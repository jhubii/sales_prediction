using Microsoft.EntityFrameworkCore;
using web_app.Data;
using web_app.Services;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllersWithViews();

// DB
builder.Services.AddDbContext<AppDbContext>(opt =>
    opt.UseSqlite(builder.Configuration.GetConnectionString("Default")));

// FastAPI options + client
builder.Services.Configure<FastApiOptions>(builder.Configuration.GetSection("FastApi"));
builder.Services.AddHttpClient<FastApiClient>();

var app = builder.Build();

app.UseStaticFiles();
app.UseRouting();

app.MapControllerRoute(
    name: "default",
    pattern: "{controller=Predictions}/{action=Create}/{id?}");

app.Run();
