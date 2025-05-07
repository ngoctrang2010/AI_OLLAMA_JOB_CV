using AI_OLLAMA_CV_JOB.Models;
using AI_OLLAMA_CV_JOB.Repository;
using Microsoft.EntityFrameworkCore;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddDbContext<AiOllamaCvJobContext>(options =>
    options.UseSqlServer(builder.Configuration.GetConnectionString("DefaultConnection")));
// Add services to the container.
builder.Services.AddControllersWithViews();
builder.Services.AddScoped<NhaTuyenDungRepository>();
builder.Services.AddScoped<CongViecRepository>();
builder.Services.AddScoped<UngVienRepository>();
builder.Services.AddScoped<ViTriLamViecRepository>();
builder.Services.AddScoped<CvUngVienRepository>();
builder.Services.AddSession();
builder.Services.AddControllersWithViews();
builder.Services.AddHttpContextAccessor();
var app = builder.Build();

// Configure the HTTP request pipeline.
if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Home/Error");
}
app.UseStaticFiles();

app.UseRouting();
app.UseSession();

app.UseAuthorization();

app.MapControllerRoute(
    name: "default",
    pattern: "{controller=Home}/{action=Index}/{id?}");
app.Run();
