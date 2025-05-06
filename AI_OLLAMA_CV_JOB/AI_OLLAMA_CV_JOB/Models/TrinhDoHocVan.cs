using System;
using System.Collections.Generic;

namespace AI_OLLAMA_CV_JOB.Models;

public partial class TrinhDoHocVan
{
    public int Id { get; set; }

    public string TenTrinhDo { get; set; } = null!;

    public virtual ICollection<CongViec> CongViecs { get; set; } = new List<CongViec>();

    public virtual ICollection<ViTriLamViec> ViTriLamViecs { get; set; } = new List<ViTriLamViec>();
}
