using AI_OLLAMA_CV_JOB.Models;
using Microsoft.EntityFrameworkCore;

namespace AI_OLLAMA_CV_JOB.Repository
{
    public class CongViecRepository
    {
        private readonly AiOllamaCvJobContext _context;

        public CongViecRepository(AiOllamaCvJobContext context)
        {
            _context = context;
        }

        // CREATE
        public async Task<bool> ThemMoiCongViec(CongViec cv)
        {
            try
            {
                if (cv == null)
                    return false;

                _context.CongViecs.Add(cv);
                await _context.SaveChangesAsync();
                return true;
            }
            catch
            {
                return false;
            }
        }

        // READ - Get all
        public async Task<IEnumerable<CongViec>> GetTatCaCongViec()
        {
            var today = DateOnly.FromDateTime(DateTime.Now);
            return await _context.CongViecs
                    .Where(p => p.HanNop == null || p.HanNop >= today)
                    .ToListAsync();
        }

        // READ - Get by ID
        public async Task<CongViec?> GetCongViecTheoId(int id)
        {
            return await _context.CongViecs.FindAsync(id);
        }

        // UPDATE
        public async Task<bool> CapNhatCongViec(CongViec updatedCv)
        {
            var existingCv = await _context.CongViecs.FindAsync(updatedCv.Id);
            if (existingCv == null)
                return false;

            existingCv.IdNtd = updatedCv.IdNtd;
            existingCv.TenCongViec = updatedCv.TenCongViec;
            existingCv.MoTaCongViec = updatedCv.MoTaCongViec;
            existingCv.YeuCauCongViec = updatedCv.YeuCauCongViec;
            existingCv.PhucLoi = updatedCv.PhucLoi;
            existingCv.DiaDiemThoiGian = updatedCv.DiaDiemThoiGian;
            existingCv.CachThucUngTuyen = updatedCv.CachThucUngTuyen;
            existingCv.KinhNghiem = updatedCv.KinhNghiem;
            existingCv.MucLuong = updatedCv.MucLuong;
            existingCv.HanNop = updatedCv.HanNop;

            await _context.SaveChangesAsync();
            return true;
        }

        // DELETE
        public async Task<bool> XoaCongViec(int id)
        {
            var cv = await _context.CongViecs.FindAsync(id);
            if (cv == null)
                return false;

            _context.CongViecs.Remove(cv);
            await _context.SaveChangesAsync();
            return true;
        }
    }
}

