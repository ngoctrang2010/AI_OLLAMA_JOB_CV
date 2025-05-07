using System;
using System.Collections.Generic;
using Microsoft.EntityFrameworkCore;

namespace AI_OLLAMA_CV_JOB.Models;

public partial class AiOllamaCvJobContext : DbContext
{
    public AiOllamaCvJobContext()
    {
    }

    public AiOllamaCvJobContext(DbContextOptions<AiOllamaCvJobContext> options)
        : base(options)
    {
    }

    public virtual DbSet<CongViec> CongViecs { get; set; }

    public virtual DbSet<CvUngVien> CvUngViens { get; set; }

    public virtual DbSet<NhaTuyenDung> NhaTuyenDungs { get; set; }

    public virtual DbSet<TrinhDoHocVan> TrinhDoHocVans { get; set; }

    public virtual DbSet<UngVien> UngViens { get; set; }

    public virtual DbSet<ViTriLamViec> ViTriLamViecs { get; set; }

    protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
#warning To protect potentially sensitive information in your connection string, you should move it out of source code. You can avoid scaffolding the connection string by using the Name= syntax to read it from configuration - see https://go.microsoft.com/fwlink/?linkid=2131148. For more guidance on storing connection strings, see https://go.microsoft.com/fwlink/?LinkId=723263.
        => optionsBuilder.UseSqlServer("Data Source=LAPTOP-V2T6O7O6\\TRANG;Initial Catalog=AI_OLLAMA_CV_JOB;User ID=sa;Password=hdkhls@2010;Connect Timeout=30;Encrypt=False;Trust Server Certificate=False;Application Intent=ReadWrite;Multi Subnet Failover=False");

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<CongViec>(entity =>
        {
            entity.ToTable("CongViec");

            entity.Property(e => e.DiaDiemThoiGian).HasColumnName("DiaDiem_ThoiGian");
            entity.Property(e => e.IdNtd).HasColumnName("Id_NTD");
            entity.Property(e => e.MucLuong).HasMaxLength(150);

            entity.HasOne(d => d.HocVanNavigation).WithMany(p => p.CongViecs)
                .HasForeignKey(d => d.HocVan)
                .HasConstraintName("FK_CongViec_TrinhDoHocVan");

            entity.HasOne(d => d.IdNtdNavigation).WithMany(p => p.CongViecs)
                .HasForeignKey(d => d.IdNtd)
                .OnDelete(DeleteBehavior.ClientSetNull)
                .HasConstraintName("FK_CongViec_NhaTuyenDung");
        });

        modelBuilder.Entity<CvUngVien>(entity =>
        {
            entity.ToTable("CV_UngVien");

            entity.Property(e => e.IdUngVien).HasColumnName("Id_UngVien");
            entity.Property(e => e.ViTriUngTuyen).HasMaxLength(200);

            entity.HasOne(d => d.IdUngVienNavigation).WithMany(p => p.CvUngViens)
                .HasForeignKey(d => d.IdUngVien)
                .OnDelete(DeleteBehavior.ClientSetNull)
                .HasConstraintName("FK_CV_UngVien_UngVien");
        });

        modelBuilder.Entity<NhaTuyenDung>(entity =>
        {
            entity.ToTable("NhaTuyenDung");
        });

        modelBuilder.Entity<TrinhDoHocVan>(entity =>
        {
            entity.ToTable("TrinhDoHocVan");

            entity.Property(e => e.TenTrinhDo).HasMaxLength(100);
        });

        modelBuilder.Entity<UngVien>(entity =>
        {
            entity.ToTable("UngVien");

            entity.Property(e => e.DuongdanCv).HasColumnName("DuongdanCV");
            entity.Property(e => e.Email).HasMaxLength(200);
            entity.Property(e => e.Sdt)
                .HasMaxLength(10)
                .IsFixedLength()
                .HasColumnName("SDT");
        });

        modelBuilder.Entity<ViTriLamViec>(entity =>
        {
            entity.ToTable("ViTriLamViec");

            entity.Property(e => e.HinhThucLamViec).HasMaxLength(100);
            entity.Property(e => e.IdUngVien).HasColumnName("Id_UngVien");
            entity.Property(e => e.LamViecTai)
                .HasMaxLength(100)
                .IsFixedLength();
            entity.Property(e => e.MucLuong).HasMaxLength(100);
            entity.Property(e => e.ViTriTuyenDung).HasMaxLength(200);

            entity.HasOne(d => d.IdUngVienNavigation).WithMany(p => p.ViTriLamViecs)
                .HasForeignKey(d => d.IdUngVien)
                .OnDelete(DeleteBehavior.ClientSetNull)
                .HasConstraintName("FK_ViTriLamViec_UngVien");

            entity.HasOne(d => d.TrinhDoNavigation).WithMany(p => p.ViTriLamViecs)
                .HasForeignKey(d => d.TrinhDo)
                .HasConstraintName("FK_ViTriLamViec_TrinhDoHocVan");
        });

        OnModelCreatingPartial(modelBuilder);
    }

    partial void OnModelCreatingPartial(ModelBuilder modelBuilder);
}
