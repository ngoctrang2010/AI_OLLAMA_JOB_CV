using AI_OLLAMA_CV_JOB.Models;
using Microsoft.EntityFrameworkCore;

namespace AI_OLLAMA_CV_JOB.Repository
{
    public class ViTriLamViecRepository
    {
        private readonly AiOllamaCvJobContext _context;
        public ViTriLamViecRepository(AiOllamaCvJobContext context)
        {
            _context = context;
        }
        public async Task<IEnumerable<ViTriLamViec>> GetTatCa()
        {
            return await _context.ViTriLamViecs.ToListAsync();
        }
    }
}
