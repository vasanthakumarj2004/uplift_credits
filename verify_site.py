"""Check the static site's route and interaction wiring without a browser."""
from pathlib import Path
from urllib.parse import urlparse, unquote
from bs4 import BeautifulSoup
import re

ROOT = Path(__file__).resolve().parent
errors = []
pages = [ROOT / 'index.html']
for slug in ['personal-loans', 'business-loans', 'home-loans', 'loan-against-property', 'about', 'faqs', 'contact', 'privacy-policy', 'terms']:
    pages.extend([ROOT / f'{slug}.html', ROOT / slug / 'index.html'])
checked = 0
for page in pages:
    doc = BeautifulSoup(page.read_text(encoding='utf-8'), 'html.parser')
    base_tag = doc.find('base')
    base = (page.parent / base_tag['href']).resolve() if base_tag else page.parent
    ids = [el['id'] for el in doc.select('[id]')]
    if len(ids) != len(set(ids)):
        errors.append(f'{page}: duplicate IDs')
    if len(doc.select('h1')) != 1:
        errors.append(f'{page}: expected exactly one h1')
    for el in doc.select('a[href], img[src], script[src], link[href]'):
        if el.name == 'link' and 'canonical' in el.get('rel', []):
            continue
        url = el.get('href', el.get('src', ''))
        parsed = urlparse(url)
        if parsed.scheme or parsed.netloc:
            continue
        if not parsed.path:
            if parsed.fragment and not doc.find(id=parsed.fragment):
                errors.append(f'{page}: missing anchor {url}')
            continue
        target = (ROOT / unquote(parsed.path).lstrip('/')) if url.startswith('/') else (base / unquote(parsed.path))
        if not target.exists():
            errors.append(f'{page}: missing {url}')
        checked += 1
    for control in doc.select('form input, form select'):
        if not control.get('name') or not doc.find('label', attrs={'for': control.get('id')}):
            errors.append(f'{page}: unlabelled or unnamed form control')
    for button in doc.select('button'):
        if not (button.find_parent('form') or any(k in button.attrs for k in ['data-apply', 'data-menu', 'data-faq', 'data-close'])):
            errors.append(f'{page}: unwired button {button.get_text(strip=True)}')
    for button in doc.select('[data-faq]'):
        panel = doc.find(id=button['aria-controls'])
        if not panel or not panel.get_text(strip=True):
            errors.append(f'{page}: FAQ answer missing')
    expected = page.parent.name if page.name == 'index.html' and page.parent != ROOT else page.stem
    if expected == 'index':
        expected = ''
    active = [a['href'] for a in doc.header.find('nav').select('a[aria-current="page"]')]
    if expected not in ['privacy-policy', 'terms'] and active != [(expected + '.html') if expected else 'index.html']:
        errors.append(f'{page}: incorrect active navigation {active}')
    loan_defaults = {'personal-loans': 'Personal Loan', 'business-loans': 'Business / MSME Loan', 'home-loans': 'Home Loan', 'loan-against-property': 'Loan Against Property'}
    if expected in loan_defaults:
        option = doc.select_one('main form [name="loanType"] option[selected]')
        if not option or option['value'] != loan_defaults[expected]:
            errors.append(f'{page}: incorrect loan default')
for css in (ROOT / 'assets').glob('*.css'):
    for url in re.findall(r'url\([\'"]?([^\)\'\"]+)', css.read_text(encoding='utf-8')):
        if not url.startswith(('http', 'data:', '#')) and not (css.parent / url).exists():
            errors.append(f'{css}: missing resource {url}')
if errors:
    raise SystemExit('\n'.join(errors))
print(f'PASS: {len(pages)} HTML entry points, {checked} local references, forms, FAQ targets, active navigation and loan selections.')
