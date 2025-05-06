using AI_OLLAMA_CV_JOB.Models;
using Microsoft.EntityFrameworkCore;

namespace AI_OLLAMA_CV_JOB.Repository
{
    public class NhaTuyenDungRepository
    {
        private readonly AiOllamaCvJobContext _context;

        public NhaTuyenDungRepository(AiOllamaCvJobContext context)
        {
            _context = context;
        }

        // CREATE
        public async Task<bool> ThemMoiNhaTuyenDung(NhaTuyenDung ntd)
        {
            try
            {
                if (ntd == null)
                    return false;

                _context.NhaTuyenDungs.Add(ntd);
                await _context.SaveChangesAsync();
                return true;
            }
            catch
            {
                return false;
            }
        }

        // READ - Get all
        public async Task<IEnumerable<NhaTuyenDung>> GetTatCaNhaTuyenDung()
        {
            return await _context.NhaTuyenDungs.ToListAsync();
        }

        // READ - Get by ID
        public async Task<NhaTuyenDung?> GetNhaTuyenDungTheoId(int id)
        {
            return await _context.NhaTuyenDungs.FindAsync(id);
        }

        // UPDATE
        public async Task<bool> CapNhatNhaTuyenDung(NhaTuyenDung updatedNtd)
        {
            var existingNtd = await _context.NhaTuyenDungs.FindAsync(updatedNtd.Id);
            if (existingNtd == null)
                return false;

            existingNtd.TenCongty = updatedNtd.TenCongty;
            existingNtd.Email = updatedNtd.Email;
            existingNtd.DiaChi = updatedNtd.DiaChi;
            existingNtd.GioiThieu = updatedNtd.GioiThieu;

            await _context.SaveChangesAsync();
            return true;
        }

        // DELETE
        public async Task<bool> XoaNhaTuyenDung(int id)
        {
            var ntd = await _context.NhaTuyenDungs.FindAsync(id);
            if (ntd == null)
                return false;

            _context.NhaTuyenDungs.Remove(ntd);
            await _context.SaveChangesAsync();
            return true;
        }
    }
}