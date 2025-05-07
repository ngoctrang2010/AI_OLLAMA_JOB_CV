using System;
using System.Collections.Generic;

namespace AI_OLLAMA_CV_JOB.Models;

public partial class CvUngVien
{
    public int Id { get; set; }

    public string ViTriUngTuyen { get; set; } = null!;

    public int HocVan { get; set; }

    public int KinhNghiem { get; set; }

    public string? DuAn { get; set; }

    public string? ChungChi { get; set; }

    public int IdUngVien { get; set; }

    public virtual UngVien IdUngVienNavigation { get; set; } = null!;
}
