using System;
using System.Collections.Generic;

namespace AI_OLLAMA_CV_JOB.Models;

public partial class CongViec
{
    public int Id { get; set; }

    public int IdNtd { get; set; }

    public string TenCongViec { get; set; } = null!;

    public string MoTaCongViec { get; set; } = null!;

    public string YeuCauCongViec { get; set; } = null!;

    public string PhucLoi { get; set; } = null!;

    public string DiaDiemThoiGian { get; set; } = null!;

    public string CachThucUngTuyen { get; set; } = null!;

    public int KinhNghiem { get; set; }

    public string MucLuong { get; set; } = null!;

    public DateOnly? HanNop { get; set; }
}
