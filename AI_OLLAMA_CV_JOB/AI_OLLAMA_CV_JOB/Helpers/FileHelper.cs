using System.Text;
using iTextSharp.text.pdf;
using iTextSharp.text.pdf.parser;
using DocumentFormat.OpenXml.Packaging;

namespace AI_OLLAMA_CV_JOB.Helpers
{
    public static class FileHelper
    {
        public static string ReadWordDocument(string path)
        {
            StringBuilder text = new StringBuilder();

            using (WordprocessingDocument doc = WordprocessingDocument.Open(path, false))
            {
                var paragraphs = doc.MainDocumentPart?.Document.Body?.Elements<DocumentFormat.OpenXml.Wordprocessing.Paragraph>();
                if (paragraphs != null)
                {
                    foreach (var paragraph in paragraphs)
                    {
                        text.AppendLine(paragraph.InnerText);
                    }
                }
            }

            return text.ToString();
        }

        public static string ExtractTextFromPdf(string path)
        {
            StringBuilder text = new StringBuilder();
            using (PdfReader reader = new PdfReader(path))
            {
                for (int i = 1; i <= reader.NumberOfPages; i++)
                {
                    text.AppendLine(PdfTextExtractor.GetTextFromPage(reader, i));
                }
            }
            return text.ToString();
        }
    }
}
