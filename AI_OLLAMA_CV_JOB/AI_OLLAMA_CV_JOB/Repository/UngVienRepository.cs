using AI_OLLAMA_CV_JOB.Models;
using Microsoft.AspNetCore.Identity;
using Microsoft.EntityFrameworkCore;

namespace AI_OLLAMA_CV_JOB.Repository
{
    public class UngVienRepository
    {
        private readonly AiOllamaCvJobContext _context;
        public UngVienRepository(AiOllamaCvJobContext context)
        {
            _context = context;
        }
        public async Task<bool> ThemMoiUngVien(UngVien uv)
        {
            try
            {
                if (uv == null)
                {
                    return false;
                }
                await _context.SaveChangesAsync();
                return true;
            }
            catch (Exception ex)
            {
                return false;
            }
        }
        public async Task<IEnumerable<UngVien>> GetUngVien()
        {
            return await _context.UngViens.ToListAsync();
        }
        public async Task<UngVien> GetUngVien(int id)
        {
            return await _context.UngViens.FindAsync(id);
        }
        public async Task<bool> UpdateUngVien(UngVien updatedUngVien)
        {
            var existingUngVien = await _context.UngViens.FindAsync(updatedUngVien.Id);
            if (existingUngVien == null)
            {
                return false;
            }

            existingUngVien.HoTen = updatedUngVien.HoTen;
            existingUngVien.Email = updatedUngVien.Email;
            existingUngVien.DuongdanCv = updatedUngVien.DuongdanCv;
            existingUngVien.KyNang = updatedUngVien.KyNang;
            existingUngVien.Sdt = updatedUngVien.Sdt;

            await _context.SaveChangesAsync();
            return true;
        }

        public async Task<UngVien?> Login(string sdt, string email)
        {
            if (string.IsNullOrEmpty(sdt) || string.IsNullOrEmpty(email))
            {
                return null;
            }

            return await _context.UngViens
                .FirstOrDefaultAsync(p => p.Sdt.Equals(sdt) && p.Email.Equals(email));
        }

    }
}
