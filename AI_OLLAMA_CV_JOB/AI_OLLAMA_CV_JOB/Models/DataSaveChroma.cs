namespace AI_OLLAMA_CV_JOB.Models
{
    public class DataSaveChroma
    {
       public class Data_UngVien_Chroma
        {
            public int Id { get; set; }
            public string? ViTriUngTuyen1 { get; set; }
            public string? KinhNghiemLamViec { get; set; }
            public string? DuAn { get; set; }
            public string? ChungChi { get; set; }
            public int Id_UngVien { get; set; }
            public string HoTen { get; set; }
            public string? DuongDanCV { get; set; }
            public string? TrinhDoHocVan { get; set; }
            public string? TimViecTai { get; set; }
            public string? HinhThucLamViec { get; set; }
            public string? MucLuong { get; set; }
            public string? ViTriUngTuyen2 { get; set; }
       }
        public class Data_CongViec_Chroma
        {
            public int Id { get; set; }
            public string? TenCongViec { get; set; }
            public string? MoTaCongViec { get; set; }
            public string? YeuCauCongViec { get; set; }
            public string? PhucLoi { get; set; }
            public string? DiaDiem { get; set; }
            public string? ThoiGianLamViec { get; set; }
            public string? CachThucUngTuyen { get; set; }
            public string? MucLuong { get; set; }
            public DateOnly? HanNop { get; set; }
            public string? TenCty { get; set; }
            public string? TrinhDoHocVan { get; set; }
            public string? YeuCauKinhNghiem { get; set; }
            public string? URLNoiQuy { get; set; }

        }
    }
}
