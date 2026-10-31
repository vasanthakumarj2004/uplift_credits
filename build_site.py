"""Rebuild the static website from the supplied homepage. Requires beautifulsoup4."""
from pathlib import Path
from copy import deepcopy
from bs4 import BeautifulSoup
import base64

ROOT = Path(__file__).resolve().parent
OUT = ROOT
ASSETS = OUT / 'assets'
ASSETS.mkdir(parents=True, exist_ok=True)
source = BeautifulSoup((ROOT / 'uplift-credits-homepage.html').read_text(encoding='utf-8'), 'html.parser')
for el in source.select('[data-tsd-source]'):
    del el['data-tsd-source']
for svg in source.select('svg[viewbox]'):
    svg['viewBox'] = svg.attrs.pop('viewbox')
for script in source.select('script'):
    script.decompose()
css = source.style.extract().text
(ASSETS / 'original.css').write_text(css, encoding='utf-8')
for name in ['original.css', 'site.css', 'fonts.css']:
    source.head.append(source.new_tag('link', rel='stylesheet', href='assets/' + name))
source.head.append(source.new_tag('script', src='assets/site.js', defer=True))
names = ['advisor', 'personal', 'business', 'home', 'property']
for name, img in zip(names, source.select('img')):
    (ASSETS / (name + '.jpg')).write_bytes(base64.b64decode(img['src'].split(',')[1]))
    img['src'] = 'assets/' + name + '.jpg'
icon = source.select_one('link[rel="icon"]')
icon['href'] = 'assets/favicon-uplift.ico'
icon['type'] = 'image/x-icon'
source.head.append(source.new_tag('link', rel='icon', type='image/svg+xml', href='assets/favicon-uplift.svg'))
for el in source.select('[aria-current], [data-status]'):
    el.attrs.pop('aria-current', None)
    el.attrs.pop('data-status', None)
    if el.has_attr('class'):
        el['class'] = [x for x in el['class'] if x != 'active']

FORM = str(source.select_one('form'))
CTA = str(source.select('main > section')[-1])
FAQ = deepcopy(source.select('main > section')[-2])
DISCLAIMER = 'Uplift Credits is a loan facilitator and assists applicants with enquiries, eligibility guidance and documentation. We are not a lender. All credit decisions are made by the respective lender.'
LOAN_TYPES = ['Personal Loan', 'Business / MSME Loan', 'Home Loan', 'Loan Against Property']
ANSWERS = [
    'Use the enquiry form to share your requirement, or contact Uplift Credits by phone or WhatsApp. A loan specialist can guide you through the next steps.',
    'Timelines depend on the lender, your eligibility, complete documentation and verification. Submitting an enquiry does not guarantee approval or a disbursal date.',
    'Document requirements vary by lender and loan type. Your specialist can explain the identity, address, income, business or property documents applicable to your enquiry.',
    'Yes. Self-employed individuals can enquire about suitable loan options. Eligibility and approval are determined by the respective lender.',
    'Uplift Credits assists with business and MSME loan enquiries, including working capital, expansion, equipment and inventory requirements, subject to lender criteria.',
    'Yes. You can enquire about a loan against residential or commercial property. Approval depends on the lender’s assessment of your profile and the property.',
    'This enquiry form does not run a credit check. Ask the specialist how the lender will assess your credit profile before proceeding with a formal application.'
]

def button(text, loan=''):
    return f'<button type="button" class="uc-button" data-apply="{loan}">{text}</button>'

def icon(name):
    paths = {
        'wallet': '<path d="M20 8V5a2 2 0 0 0-2-2H5a3 3 0 0 0 0 6h15v11H5a3 3 0 0 1-3-3V6"/><path d="M20 12h-4a2 2 0 0 0 0 4h4"/><path d="M17 14h.01"/>',
        'trending-up': '<path d="m3 17 6-6 4 4 8-10"/><path d="M15 5h6v6"/>',
        'factory': '<path d="M2 20V4a1 1 0 0 1 1-1h3a1 1 0 0 1 1 1v9l7-4v4l8-4v11a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1Z"/><path d="M7 17v1m5-1v1m5-1v1"/>',
        'boxes': '<path d="m12 2 5 3v6l-5 3-5-3V5l5-3Zm0 6v6M7 5l5 3 5-3M7 10l-5 3v6l5 3 5-3v-5M2 13l5 3 5-3M7 16v6m10-12 5 3v6l-5 3-5-3m0-6 5 3 5-3m-5 3v6"/>',
        'target': '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
        'compass': '<circle cx="12" cy="12" r="10"/><path d="m16 8-2.5 5.5L8 16l2.5-5.5L16 8Z"/>',
        'check': '<path d="m5 12 4 4L19 6"/>'
    }
    return f'<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{paths[name]}</svg>'

def checks(items):
    return '<ul class="uc-checks">' + ''.join(f'<li><span aria-hidden="true">{icon("check")}</span>{x}</li>' for x in items) + '</ul>'

def hero(label, title, paragraphs, image=None):
    copy = f'<div><p class="uc-eyebrow">{label}</p><h1>{title}</h1>' + ''.join(f'<p class="uc-lead">{p}</p>' for p in paragraphs) + '</div>'
    photo = f'<img class="uc-hero-photo" src="assets/{image}.jpg" alt="{dict(personal="Loan specialist advising a couple", business="Business owner reviewing inventory", home="Family at their new home", property="Residential property", advisor="Uplift Credits loan specialist advising a couple")[image]}" width="750" height="600">' if image else ''
    return f'<section class="uc-hero"><div class="container-page {"uc-two" if image else "uc-heading"}">{copy}{photo}</div></section>'

def enquiry(title, subtitle, loan):
    form = BeautifulSoup(FORM, 'html.parser')
    for opt in form.select('option'):
        if opt.get('value') == loan:
            opt['selected'] = ''
    return f'<section class="uc-enquiry" id="enquiry"><div class="container-page uc-two"><div><h2>{title}</h2><p class="uc-lead">{subtitle}</p><p class="uc-disclaimer">{DISCLAIMER}</p></div>{form}</div></section>'

def pair(left, right):
    return f'<section class="uc-section"><div class="container-page uc-two">{left}{right}</div></section>'

pages = {}
pages['personal-loans'] = ('Personal Loans', hero('Personal loans', 'Personal Loans With Faster Assistance', ["When you need funds, waiting shouldn’t add to your stress.", 'Uplift Credits helps you explore personal loan options based on your income, credit profile and financial requirements.'], 'personal') + pair(
    '<div><h2>Why Consider a Personal Loan?</h2>' + checks(['Unsecured financing options*', 'Quick application process', 'Flexible loan amounts*', 'Flexible repayment tenure*', 'Simple documentation*', 'Dedicated application support']) + '</div>',
    '<div><h2>Who Can Apply?</h2>' + checks(['Salaried professionals', 'Self-employed individuals', 'Business owners', 'Eligible professionals']) + '<p class="uc-note">*Loan amount, tenure and documentation requirements are determined by the lender and are subject to eligibility and verification.</p>' + button('Check Your Personal Loan Eligibility', LOAN_TYPES[0]) + '</div>') + enquiry('Start Your Personal Loan Enquiry', 'Share your requirement and our loan specialist will get in touch with you.', LOAN_TYPES[0]))

funding = [('Working Capital', 'Manage day-to-day operational expenses and cash-flow requirements.', 'wallet'), ('Business Expansion', 'Finance expansion, new locations or growth initiatives.', 'trending-up'), ('Equipment & Machinery', 'Explore financing for eligible business assets and equipment.', 'factory'), ('Inventory & Stock', 'Support inventory and operational requirements.', 'boxes')]
cards = ''.join(f'<article class="uc-card"><span class="uc-icon">{icon(icon_name)}</span><h3>{title}</h3><p>{desc}</p></article>' for title, desc, icon_name in funding)
pages['business-loans'] = ('Business Loans', hero('Business / MSME loans', 'Business Funding That Keeps You Moving', ['A growing business needs access to capital at the right time.', 'Uplift Credits helps MSMEs and business owners explore financing options for working capital, expansion and other business requirements.'], 'business') + f'<section class="uc-section"><div class="container-page"><div class="uc-center"><p class="uc-eyebrow">Funding areas</p><h2>Where Business Funding Helps</h2></div><div class="uc-card-grid">{cards}</div><div class="uc-center">{button("Apply for Business Loan", LOAN_TYPES[1])}</div></div></section>' + enquiry('Get Business Loan Assistance', 'Tell us about your business requirement and our specialist will call you back.', LOAN_TYPES[1]))

pages['home-loans'] = ('Home Loans', hero('Home loans', 'Your Home. Your Future.<br>Our Guidance.', ['Buying a home is a major financial decision. Uplift Credits helps simplify the home loan journey — from initial enquiry to application support.'], 'home') + pair(
    '<div><h2>Home Loan Solutions</h2>' + checks(['New Home Purchase', 'Resale Property', 'Construction Finance*', 'Home Loan Balance Transfer*', 'Eligible Property Financing']) + '<p class="uc-note">*Availability depends on the lender, property type and applicant eligibility. Terms and conditions apply.</p></div>',
    '<div class="uc-panel"><h3>Guidance at every stage of your home loan</h3>' + checks(['Understand your home loan eligibility', 'Documentation assistance', 'Application support until sanction', 'Clarity on applicable terms before you proceed']) + button('Start Your Home Loan Enquiry', LOAN_TYPES[2]) + '</div>') + enquiry('Start Your Home Loan Enquiry', 'Share a few details and our loan specialist will guide you through the next steps.', LOAN_TYPES[2]))

pages['loan-against-property'] = ('Loan Against Property', hero('Loan against property', 'Turn Your Property Into Financial Opportunity', ['Have a residential or commercial property? A Loan Against Property may help you access funds while retaining ownership and use of your property, subject to lender terms.'], 'property') + pair(
    '<div><h2>Use Funds For</h2>' + checks(['Business expansion', 'Working capital', 'Education', 'Medical expenses', 'Debt consolidation', 'Major personal requirements']) + '</div>',
    '<div class="uc-panel"><h3>What to expect</h3>' + checks(['Property and profile based eligibility assessment', 'Guidance on required property and income documents', 'Support through valuation and legal verification stages', 'Clear explanation of applicable lender terms']) + button('Check LAP Eligibility', LOAN_TYPES[3]) + '</div>') + enquiry('Check Your LAP Eligibility', 'Tell us about your property and requirement — our specialist will call you back.', LOAN_TYPES[3]))

pages['about'] = ('About Us', hero('About us', 'Making Credit Simpler.<br>Making Opportunities Possible.', ['Uplift Credits is focused on making the loan journey simpler, faster and more accessible for individuals and businesses.', 'We understand that every borrower has different financial needs. That’s why our approach begins by understanding your requirement and helping you navigate suitable loan solutions.', 'From personal finance to business funding, home loans and loans against property, our team provides guidance throughout the application journey.'], 'advisor') + '<section class="uc-section"><div class="container-page uc-two uc-mission-grid">' + f'<article class="uc-card uc-mission"><span class="uc-icon">{icon("target")}</span><h3>Mission</h3><p>To simplify access to credit through faster assistance, clear guidance and customer-focused service.</p></article><article class="uc-card uc-mission"><span class="uc-icon green">{icon("compass")}</span><h3>Vision</h3><p>To become a trusted financial solutions brand that helps individuals and businesses move forward with confidence.</p></article></div></section>')

faq = deepcopy(FAQ)
faq.select_one('.container-page').find('div', recursive=False).decompose()
faq.select_one('.container-page').find('div', recursive=False)['class'] = 'uc-faq-list'
pages['faqs'] = ('FAQs', hero('FAQs', 'Frequently Asked Questions', ['Clear answers on how enquiries, eligibility, documentation and lender approvals work at Uplift Credits.']) + str(faq))

contacts = [ ('Phone', '+91 90000 00000', 'tel:+919000000000', 'phone'), ('WhatsApp', 'Chat with our team', 'https://wa.me/919000000000', 'message-circle'), ('Email', 'hello@upliftcredits.com', 'mailto:hello@upliftcredits.com', 'mail'), ('Address', 'Office address, City, State — PIN', '', 'map-pin') ]
contact_cards = ''
for label, value, link, icon_name in contacts:
    icon_svg = deepcopy(source.select_one('footer .lucide-' + icon_name))
    icon_svg['class'] = 'uc-contact-icon'
    tag = 'a' if link else 'div'
    attrs = f' href="{link}"' if link else ''
    contact_cards += f'<{tag}{attrs} class="uc-contact-card"><span class="uc-icon {"green" if label == "WhatsApp" else ""}">{icon_svg}</span><span><span class="uc-contact-label">{label}</span><strong>{value}</strong></span></{tag}>'
pages['contact'] = ('Contact', f'<section class="uc-contact"><div class="container-page uc-contact-grid"><div><p class="uc-eyebrow">Contact</p><h1>Talk to a Loan Specialist</h1><p class="uc-lead">Reach us on call or WhatsApp, or submit your enquiry and we’ll get back to you.</p><div class="uc-contacts">{contact_cards}</div></div>{FORM}</div></section>')

# These routes exist in the supplied footer, but their contents are not in the video.
pages['privacy-policy'] = ('Privacy Policy', hero('Website information', 'Privacy Policy', ['The approved privacy policy has not yet been supplied.']) + '<section class="uc-section"><div class="container-page uc-legal"><h2>Enquiry form information</h2><p>The enquiry form prepares a WhatsApp message containing the details you enter. You review and send the message in WhatsApp. This static website does not save your enquiry to a database.</p><p>For information about how Uplift Credits handles enquiries after receiving them, please contact the team before submitting personal information.</p><a class="uc-button" href="contact.html">Contact Uplift Credits</a></div></section>')
pages['terms'] = ('Terms & Conditions', hero('Website information', 'Terms &amp; Conditions', ['The approved terms and conditions have not yet been supplied.']) + f'<section class="uc-section"><div class="container-page uc-legal"><h2>Loan facilitation</h2><p>{DISCLAIMER}</p><p>Loan approval, interest rate, loan amount, tenure, processing fees and disbursal are determined by the respective lender based on its eligibility criteria, credit assessment, documentation and other applicable terms. Submission of an enquiry does not guarantee loan approval or disbursal.</p><a class="uc-button" href="contact.html">Contact Uplift Credits</a></div></section>')

def write_page(slug, title, content=None):
    doc = deepcopy(source)
    doc.title.string = f'{title} | Uplift Credits' if slug else 'Uplift Credits | Fast Personal, Business & Home Loans'
    if content is not None:
        doc.main.clear()
        doc.main.append(BeautifulSoup(content + CTA, 'html.parser'))
    doc.main['id'] = 'main-content'
    doc.body.insert(0, BeautifulSoup('<a class="uc-skip" href="#main-content">Skip to content</a>', 'html.parser'))
    for i, (btn, answer) in enumerate(zip(doc.select('button[aria-controls]'), ANSWERS)):
        panel = doc.find(id=btn['aria-controls'])
        if panel:
            panel.clear()
            panel.append(BeautifulSoup(f'<p class="uc-faq-answer">{answer}</p>', 'html.parser'))
            btn['data-faq'] = ''
    for btn in doc.select('button'):
        if btn.find_parent('form') or btn.has_attr('data-faq'):
            continue
        if btn.get('aria-label') == 'Open menu':
            btn['data-menu'] = ''
            btn['aria-controls'] = 'mobile-menu'
            btn.attrs.pop('aria-haspopup', None)
            continue
        if not btn.has_attr('data-apply'):
            txt = btn.get_text(' ', strip=True).lower()
            loan = next((x for x, keyword in zip(LOAN_TYPES, ['personal', 'business', 'home loan', 'property']) if keyword in txt), '')
            btn['data-apply'] = loan
        btn['type'] = 'button'
    mobile_nav = deepcopy(doc.header.nav)
    doc.header.nav['aria-label'] = 'Main navigation'
    mobile_nav['id'] = 'mobile-menu'
    mobile_nav['class'] = 'uc-mobile-menu'
    mobile_nav['hidden'] = ''
    mobile_nav['aria-label'] = 'Mobile navigation'
    doc.header.append(mobile_nav)
    for a in doc.select('a[href^="/"]'):
        target = a['href'].strip('/')
        a['href'] = target + '.html' if target else 'index.html'
        if target == slug:
            a['aria-current'] = 'page'
            a['data-status'] = 'active'
    modal = BeautifulSoup(f'<dialog id="apply-dialog" aria-labelledby="apply-title"><div class="uc-dialog-head"><h2 id="apply-title">Apply for a Loan</h2><button type="button" data-close aria-label="Close application form">×</button></div>{FORM}</dialog>', 'html.parser')
    doc.body.append(modal)
    for i, form in enumerate(doc.select('form')):
        form['data-enquiry'] = ''
        for control in form.select('[data-field]'):
            field_id = f'form-{i}-{control["data-field"]}'
            control['id'] = field_id
            control['name'] = control['data-field']
            label = control.parent.find('label')
            if label:
                label['for'] = field_id
        status = doc.new_tag('p', attrs={'class': 'uc-form-status', 'role': 'status'})
        form.append(status)
    path = '/' + slug if slug else '/'
    doc.select_one('link[rel="canonical"]')['href'] = path
    doc.select_one('meta[property="og:url"]')['content'] = path
    doc.select_one('meta[property="og:title"]')['content'] = doc.title.string
    if content:
        description = BeautifulSoup(content, 'html.parser').select_one('.uc-lead')
        if description:
            for selector in ['meta[name="description"]', 'meta[property="og:description"]']:
                doc.select_one(selector)['content'] = description.get_text(' ', strip=True)
    text = str(doc)
    (OUT / (slug + '.html' if slug else 'index.html')).write_text(text, encoding='utf-8')
    if slug:
        folder = OUT / slug
        folder.mkdir(exist_ok=True)
        doc.head.insert(0, doc.new_tag('base', href='../'))
        (folder / 'index.html').write_text(str(doc), encoding='utf-8')

write_page('', 'Home')
for slug, (title, content) in pages.items():
    write_page(slug, title, content)
print(f'Built {len(pages) + 1} pages in {OUT}')
