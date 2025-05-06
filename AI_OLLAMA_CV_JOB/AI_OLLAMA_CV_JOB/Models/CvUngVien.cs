using System;
using System.Collections.Generic;

namespace AI_OLLAMA_CV_JOB.Models;

public partial class CvUngVien
{
    public int Id { get; set; }

    public string ViTriUngTuyen { get; set; } = null!;

    public string HocVan { get; set; } = null!;

    public string KinhNghiem { get; set; } = null!;

    public string? DuAn { get; set; }

    public string ChungChi { get; set; } = null!;

    public int IdUngVien { get; set; }

    public virtual UngVien IdUngVienNavigation { get; set; } = null!;
}
