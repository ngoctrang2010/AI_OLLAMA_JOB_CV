using System;
using System.Collections.Generic;

namespace AI_OLLAMA_CV_JOB.Models;

public partial class NoiQuyCty
{
    public int Id { get; set; }

    public int IdCty { get; set; }

    public string Noidung { get; set; } = null!;

    public virtual NhaTuyenDung IdCtyNavigation { get; set; } = null!;
}
