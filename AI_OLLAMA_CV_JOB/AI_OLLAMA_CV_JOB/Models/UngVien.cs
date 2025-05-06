using System;
using System.Collections.Generic;

namespace AI_OLLAMA_CV_JOB.Models;

public partial class UngVien
{
    public int Id { get; set; }

    public string HoTen { get; set; } = null!;

    public string Email { get; set; } = null!;

    public string? DuongdanCv { get; set; }

    public string? KyNang { get; set; }

    public string Sdt { get; set; } = null!;

    public virtual ICollection<CvUngVien> CvUngViens { get; set; } = new List<CvUngVien>();

    public virtual ICollection<ViTriLamViec> ViTriLamViecs { get; set; } = new List<ViTriLamViec>();
}
