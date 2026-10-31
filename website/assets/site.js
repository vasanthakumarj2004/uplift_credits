(() => {
  'use strict';
  const dialog = document.getElementById('apply-dialog');
  const menu = document.getElementById('mobile-menu');
  const menuButton = document.querySelector('[data-menu]');
  let opener;
  let previousOverflow = '';

  function closeMenu() {
    menu.hidden = true;
    menuButton.setAttribute('aria-expanded', 'false');
    menuButton.setAttribute('aria-label', 'Open menu');
  }

  document.addEventListener('click', (event) => {
    const apply = event.target.closest('[data-apply]');
    if (apply) {
      opener = apply;
      const form = dialog.querySelector('form');
      form.reset();
      clearErrors(form);
      form.querySelector('[role="status"]').replaceChildren();
      form.elements.loanType.value = apply.dataset.apply || '';
      closeMenu();
      previousOverflow = document.body.style.overflow;
      dialog.showModal();
      document.body.style.overflow = 'hidden';
      form.elements.fullName.focus({preventScroll: true});
      return;
    }
    if (event.target.closest('[data-close]')) dialog.close();
    const faq = event.target.closest('[data-faq]');
    if (faq) {
      const open = faq.getAttribute('aria-expanded') !== 'true';
      const group = faq.closest('section');
      group.querySelectorAll('[data-faq]').forEach(button => {
        const expanded = button === faq && open;
        button.setAttribute('aria-expanded', String(expanded));
        button.dataset.state = expanded ? 'open' : 'closed';
        const panel = document.getElementById(button.getAttribute('aria-controls'));
        panel.hidden = !expanded;
        panel.dataset.state = expanded ? 'open' : 'closed';
        panel.style.animation = 'none';
      });
      return;
    }
    if (event.target.closest('[data-menu]')) {
      menu.hidden = !menu.hidden;
      menuButton.setAttribute('aria-expanded', String(!menu.hidden));
      menuButton.setAttribute('aria-label', menu.hidden ? 'Open menu' : 'Close menu');
    } else if (!event.target.closest('header')) closeMenu();
  });

  dialog.addEventListener('click', event => {
    const rect = dialog.getBoundingClientRect();
    if (event.target === dialog && (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom)) dialog.close();
  });
  dialog.addEventListener('close', () => {
    document.body.style.overflow = previousOverflow;
    opener?.focus({preventScroll: true});
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && !menu.hidden) {
      closeMenu();
      menuButton.focus();
    }
  });

  function clearErrors(form) {
    form.querySelectorAll('.uc-field-error').forEach(el => el.remove());
    form.querySelectorAll('[aria-invalid]').forEach(el => {
      el.removeAttribute('aria-invalid');
      el.removeAttribute('aria-describedby');
    });
  }
  function numeric(value) {
    return /^\d[\d, ]*$/.test(value) && Number(value.replace(/[, ]/g, '')) > 0;
  }
  document.querySelectorAll('[data-enquiry]').forEach(form => {
    const mobile = form.elements.mobile;
    mobile.maxLength = 10;
    mobile.addEventListener('input', () => { mobile.value = mobile.value.replace(/\D/g, '').slice(0, 10); });
    form.addEventListener('submit', event => {
      event.preventDefault();
      clearErrors(form);
      const value = Object.fromEntries(new FormData(form));
      Object.keys(value).forEach(key => { value[key] = value[key].trim(); });
      const errors = {};
      if ('fullName' in value && value.fullName.length < 2) errors.fullName = 'Please enter your full name.';
      if (!value.loanType) errors.loanType = 'Select a loan type.';
      if (!numeric(value.amount)) errors.amount = 'Enter a valid loan amount greater than zero.';
      if ('income' in value && !numeric(value.income)) errors.income = 'Enter your monthly income or turnover.';
      if (!value.employment) errors.employment = 'Select your employment type.';
      if (!/^[6-9]\d{9}$/.test(value.mobile)) errors.mobile = 'Enter a valid 10-digit mobile number.';
      if (value.city.length < 2) errors.city = 'Please enter your city.';
      const status = form.querySelector('[role="status"]');
      status.replaceChildren();
      for (const [name, message] of Object.entries(errors)) {
        const field = form.elements[name];
        const error = document.createElement('p');
        error.id = field.id + '-error';
        error.className = 'uc-field-error';
        error.textContent = message;
        field.setAttribute('aria-invalid', 'true');
        field.setAttribute('aria-describedby', error.id);
        field.after(error);
      }
      if (Object.keys(errors).length) {
        status.textContent = 'Please check the highlighted fields.';
        form.elements[Object.keys(errors)[0]].focus();
        return;
      }
      const lines = ['New loan enquiry — Uplift Credits'];
      const labels = {fullName: 'Name', loanType: 'Loan type', amount: 'Required amount', income: 'Monthly income / turnover', employment: 'Employment', mobile: 'Mobile', city: 'City'};
      for (const [key, label] of Object.entries(labels)) if (value[key]) lines.push(label + ': ' + value[key]);
      const url = 'https://wa.me/919000000000?text=' + encodeURIComponent(lines.join('\n'));
      status.append('Your enquiry is ready. Review and send it in WhatsApp to contact the team. ');
      const link = document.createElement('a');
      link.href = url;
      link.target = '_blank';
      link.rel = 'noopener noreferrer';
      link.textContent = 'Continue to WhatsApp';
      status.append(link);
      // Explicit handoff: nothing is sent or stored by this website.
      link.focus();
    });
  });
})();
