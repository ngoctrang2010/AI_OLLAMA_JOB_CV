using AI_OLLAMA_CV_JOB.Models;
using Microsoft.EntityFrameworkCore;

namespace AI_OLLAMA_CV_JOB.Repository
{
    public class CvUngVienRepository
    {
        private readonly AiOllamaCvJobContext _context;
        public CvUngVienRepository(AiOllamaCvJobContext context)
        {
            _context = context;
        }
        public async Task<IEnumerable<CvUngVien>> GetTatCaCV()
        {
            return await _context.CvUngViens.ToListAsync();
        }
    }
}
