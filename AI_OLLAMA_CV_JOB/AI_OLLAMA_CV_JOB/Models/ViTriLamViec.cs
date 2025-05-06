using System;
using System.Collections.Generic;

namespace AI_OLLAMA_CV_JOB.Models;

public partial class ViTriLamViec
{
    public int Id { get; set; }

    public int IdUngVien { get; set; }

    public string? ViTriTuyenDung { get; set; }

    public string? LamViecTai { get; set; }

    public string? HinhThucLamViec { get; set; }

    public int? TrinhDo { get; set; }

    public string? MucLuong { get; set; }

    public int? HocVan { get; set; }

    public virtual UngVien IdUngVienNavigation { get; set; } = null!;

    public virtual TrinhDoHocVan? TrinhDoNavigation { get; set; }
}
