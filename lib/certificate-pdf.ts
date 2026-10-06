/**
 * Save a certificate card as a one-page PDF.
 *
 * The card is drawn by the browser into an image (html-to-image) and placed on
 * an A4 landscape page (pdf-lib). Drawing through the browser is deliberate: a
 * learner's name can be in any script, and the browser already has fonts for
 * it, whereas PDF's built-in fonts cover Latin only. The verification link is
 * added under the image as real text, so it can be clicked and copied.
 *
 * Both libraries are imported on demand: nobody pays for them until they
 * press Download.
 */
export async function downloadCertificatePdf(
  card: HTMLElement,
  opts: { certificateId: string; verifyUrl: string; fileName: string },
): Promise<void> {
  const [{ toPng }, { PDFDocument, StandardFonts, rgb }] = await Promise.all([
    import("html-to-image"),
    import("pdf-lib"),
  ]);

  const background =
    getComputedStyle(document.body).backgroundColor || "#ffffff";
  const png = await toPng(card, {
    pixelRatio: 2,
    backgroundColor: background,
    // The buttons under the card are for the screen, not the certificate.
    filter: (node) =>
      !(node instanceof HTMLElement && node.classList.contains("pch-cert__actions")),
  });

  const pdf = await PDFDocument.create();
  pdf.setTitle(`Certificate ${opts.certificateId}`);
  pdf.setCreator("Python Central Hub");
  const page = pdf.addPage([841.89, 595.28]); // A4 landscape, in points
  const image = await pdf.embedPng(png);

  const margin = 40;
  const footer = 36;
  const maxW = page.getWidth() - margin * 2;
  const maxH = page.getHeight() - margin * 2 - footer;
  const scale = Math.min(maxW / image.width, maxH / image.height);
  const w = image.width * scale;
  const h = image.height * scale;
  page.drawImage(image, {
    x: (page.getWidth() - w) / 2,
    y: margin + footer + (maxH - h) / 2,
    width: w,
    height: h,
  });

  const font = await pdf.embedFont(StandardFonts.Helvetica);
  const line = `Verify this certificate at ${opts.verifyUrl}`;
  const size = 10;
  page.drawText(line, {
    x: (page.getWidth() - font.widthOfTextAtSize(line, size)) / 2,
    y: margin,
    size,
    font,
    color: rgb(0.35, 0.38, 0.44),
  });

  const bytes = await pdf.save();
  const url = URL.createObjectURL(new Blob([bytes as BlobPart], { type: "application/pdf" }));
  const link = document.createElement("a");
  link.href = url;
  link.download = opts.fileName;
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 10_000);
}
