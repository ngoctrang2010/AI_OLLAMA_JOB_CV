using System;
using System.Collections.Generic;

namespace AI_OLLAMA_CV_JOB.Models;

public partial class NhaTuyenDung
{
    public int Id { get; set; }

    public string? TenCongty { get; set; }

    public string? Email { get; set; }

    public string? DiaChi { get; set; }

    public string? GioiThieu { get; set; }
  
    public string? DuongDanTep { get; set; }

    public virtual ICollection<CongViec> CongViecs { get; set; } = new List<CongViec>();

    public virtual ICollection<NoiQuyCty> NoiQuyCties { get; set; } = new List<NoiQuyCty>();
}
