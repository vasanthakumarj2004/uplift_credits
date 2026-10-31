# Uplift Credits website

Open **index.html in this folder** in your browser. All navigation works directly from the files, including when the folder is moved. No installation or build is required to view the website.

The original `uplift-credits-homepage.html` and `reference_video1.mp4` are preserved. The finished HTML pages are directly in this folder; images, fonts, styles and JavaScript are stored locally in `assets/`. The earlier `website/` subfolder is a previous build; use the root `index.html` for the current version.

The reference was reviewed frame by frame for the loan, About, FAQ and Contact pages and application popup. This revision aligns the card and list spacing, SVG icons, Mission/Vision typography, dialog padding and brand colors with the recording. The supplied file is `reference_video1.mp4`; no `.mp5` file is present.

## Pages

- Home
- Personal Loans
- Business / MSME Loans
- Home Loans
- Loan Against Property
- About Us
- FAQs
- Contact
- Privacy Policy (approved content still needed)
- Terms & Conditions (approved content still needed)

Each page has a `.html` route for direct file use and a directory route, such as `/personal-loans/`, for static hosting. Header and footer navigation use relative links, so browser Back/Forward and direct page refresh work without a client-side router or server rewrites.

## Interactions

Application buttons open the enquiry popup. Loan-specific buttons preselect the loan type. Escape, the close button and clicking the backdrop dismiss the popup. FAQ questions expand individually. Small-screen navigation has a working menu. Forms validate fields and prepare a WhatsApp message; the visitor then follows **Continue to WhatsApp** to review and send it. No enquiry is sent automatically, stored in the browser or saved to a backend.

## Details still needed before launch

The supplied HTML and video contain a placeholder phone/WhatsApp number (`+91 90000 00000`), email (`hello@upliftcredits.com`) and office address. These have been retained. Replace them in `build_site.py`, the supplied homepage and `assets/site.js`, then rebuild.

The video does not show Privacy Policy, Terms & Conditions, or expanded FAQ answers. Policy pages explicitly identify the missing approved copy; their explanatory text is limited to implemented form behavior and the original loan disclaimer. FAQ answers were added to make the accordions usable and should be reviewed with the business.

## Local server (optional)

From this folder, run:

```powershell
python -m http.server 8000 --bind 127.0.0.1
```

Then visit `http://127.0.0.1:8000/`. Stop the server with Ctrl+C.

## Rebuild and verify

`build_site.py` uses the original homepage as the source for the shared header, footer, forms, home content and original styles. It requires Python and `beautifulsoup4`. The custom CSS, JS and downloaded fonts are retained when rebuilding.

```powershell
python build_site.py
python verify_site.py
node --check assets/site.js
```

Validation checks every page, internal link, local image/font/style/script, form label, FAQ target and modal trigger. Browser visual and interaction QA was unavailable in the execution environment; the layouts were reconstructed from sampled video frames and the supplied HTML.
