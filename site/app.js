const CONFIG = {
  apiBase: 'https://ia-over-production.up.railway.app',
  productName: 'GolScope Premium',
  currency: 'BRL'
};

const pricingState = {
  normalCents: null,
  the100Cents: null,
  confirmed: 0,
  reserved: 0,
  remaining: null,
  campaignState: 'IDLE'
};

let activeCoupon = '';
let currentTotalCents = null;
let modalAction = null;

const $ = (selector) => document.querySelector(selector);
const moneyCents = (cents) => new Intl.NumberFormat('pt-BR', {
  style: 'currency',
  currency: CONFIG.currency
}).format(Number(cents || 0) / 100);

function formatCpf(value) {
  const digits = String(value || '').replace(/\D/g, '').slice(0, 11);
  if (digits.length <= 3) return digits;
  if (digits.length <= 6) return `${digits.slice(0, 3)}.${digits.slice(3)}`;
  if (digits.length <= 9) return `${digits.slice(0, 3)}.${digits.slice(3, 6)}.${digits.slice(6)}`;
  return `${digits.slice(0, 3)}.${digits.slice(3, 6)}.${digits.slice(6, 9)}-${digits.slice(9)}`;
}

function formatPhone(value) {
  const digits = String(value || '').replace(/\D/g, '').slice(0, 11);
  if (!digits) return '';
  if (digits.length <= 2) return `(${digits}`;
  const area = digits.slice(0, 2);
  const number = digits.slice(2);
  if (number.length <= 4) return `(${area}) ${number}`;
  if (number.length <= 8) return `(${area}) ${number.slice(0, 4)}-${number.slice(4)}`;
  return `(${area}) ${number.slice(0, 5)}-${number.slice(5, 9)}`;
}

function installInputMasks() {
  const cpf = $('#cpf');
  const phone = $('#phone');
  if (cpf) {
    cpf.maxLength = 14;
    cpf.addEventListener('input', () => { cpf.value = formatCpf(cpf.value); });
  }
  if (phone) {
    phone.maxLength = 15;
    phone.addEventListener('input', () => { phone.value = formatPhone(phone.value); });
  }
}

function buyerPayload() {
  return {
    name: $('#name')?.value.trim() || '',
    email: $('#email')?.value.trim() || '',
    phone: $('#phone')?.value.trim() || '',
    cpf: $('#cpf')?.value.trim() || ''
  };
}

function validateBuyer() {
  const required = ['name', 'email', 'phone', 'cpf'];
  let firstInvalid = null;
  required.forEach((id) => {
    const input = $(`#${id}`);
    if (!input) return;
    const invalid = !input.value.trim();
    input.style.borderColor = invalid ? '#ef4444' : '';
    if (invalid && !firstInvalid) firstInvalid = input;
  });
  if (firstInvalid) {
    firstInvalid.focus();
    firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
    return false;
  }
  return true;
}

function setText(selector, value) {
  const el = $(selector);
  if (el) el.textContent = value;
}

function applyCampaignCounts(data = {}) {
  if (Number.isFinite(Number(data.confirmed))) pricingState.confirmed = Number(data.confirmed);
  if (Number.isFinite(Number(data.reserved))) pricingState.reserved = Number(data.reserved);
  if (Number.isFinite(Number(data.remaining))) pricingState.remaining = Number(data.remaining);
  updateCampaignAvailability();
}

function updateCampaignAvailability() {
  const el = $('#the100Availability');
  if (!el) return;
  el.classList.remove('sold-out', 'reserved');
  if (pricingState.campaignState === 'RESERVED' || pricingState.campaignState === 'PAYMENT_PENDING') {
    el.classList.add('reserved');
    el.textContent = pricingState.campaignState === 'PAYMENT_PENDING'
      ? 'Sua vaga THE100 está vinculada ao checkout em andamento.'
      : 'Sua vaga THE100 está reservada temporariamente.';
    return;
  }
  if (pricingState.remaining === null) {
    el.textContent = 'Consultando vagas reais...';
    return;
  }
  if (pricingState.remaining <= 0) {
    el.classList.add('sold-out');
    el.textContent = 'THE100 esgotado — as 100 vagas foram preenchidas ou estão reservadas.';
    return;
  }
  el.textContent = `${pricingState.remaining} ${pricingState.remaining === 1 ? 'vaga disponível' : 'vagas disponíveis'} agora · ${pricingState.confirmed} confirmadas`;
}

function updateSummary() {
  const normal = pricingState.normalCents;
  const charged = currentTotalCents ?? normal;
  setText('#subtotal', normal === null ? '—' : moneyCents(normal));
  setText('#total', charged === null ? '—' : moneyCents(charged));
  setText('#normalPriceInline', normal === null ? 'carregando...' : `${moneyCents(normal)}/mês`);
  setText('#the100PriceInline', pricingState.the100Cents === null ? 'R$ 100,00' : moneyCents(pricingState.the100Cents));
  setText('#paymentPriceBadge', charged === null ? 'Carregando preço...' : `${moneyCents(charged)}/mês`);
  const line = $('#discountLine');
  if (line) {
    if (normal !== null && charged !== null && charged < normal) {
      line.classList.remove('hidden');
      setText('#discountValue', moneyCents(charged));
    } else {
      line.classList.add('hidden');
    }
  }
}

function showCouponFeedback(message, type = '') {
  const el = $('#couponFeedback');
  if (!el) return;
  el.textContent = message;
  el.className = `coupon-feedback ${type}`;
}

function setBusy(button, busy, busyText) {
  if (!button) return;
  if (busy) {
    button.dataset.originalText = button.textContent;
    button.disabled = true;
    button.textContent = busyText;
  } else {
    button.disabled = false;
    button.textContent = button.dataset.originalText || button.textContent;
  }
}

async function api(path, options = {}) {
  const response = await fetch(`${CONFIG.apiBase}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {})
    }
  });
  let data = {};
  try {
    data = await response.json();
  } catch (_) {
    data = {};
  }
  if (!response.ok) {
    const error = new Error(data.error || data.message || 'Não foi possível concluir a operação.');
    error.code = data.code || '';
    error.data = data;
    error.status = response.status;
    throw error;
  }
  return data;
}

async function loadPricing() {
  try {
    const data = await api('/checkout/pricing', { method: 'GET' });
    pricingState.normalCents = Number(data.normal_monthly_price_cents);
    pricingState.the100Cents = Number(data.the100_monthly_price_cents);
    const campaign = data.campaign || {};
    applyCampaignCounts(campaign);
    if (!activeCoupon) currentTotalCents = pricingState.normalCents;
    updateSummary();
  } catch (_) {
    showCouponFeedback('Não foi possível carregar a condição comercial agora. O backend continuará validando o valor no checkout.', 'warning');
  }
}

function applyQuote(data) {
  if (Number.isFinite(Number(data.normal_monthly_price_cents))) pricingState.normalCents = Number(data.normal_monthly_price_cents);
  if (Number.isFinite(Number(data.charged_monthly_price_cents))) currentTotalCents = Number(data.charged_monthly_price_cents);
  if (data.campaign_code === 'THE100' && pricingState.the100Cents === null) pricingState.the100Cents = Number(data.charged_monthly_price_cents);
  pricingState.campaignState = data.campaign_state || pricingState.campaignState;
  applyCampaignCounts(data);
  updateSummary();
}

function showModal(title, text, action = null) {
  setText('#modalTitle', title);
  setText('#modalText', text);
  modalAction = action;
  const button = $('#modalOk');
  if (button) button.textContent = action?.label || 'Entendi';
  $('#modal')?.classList.remove('hidden');
}

function closeModal() {
  $('#modal')?.classList.add('hidden');
  modalAction = null;
  setText('#modalOk', 'Entendi');
}

async function applyCoupon() {
  if (!validateBuyer()) {
    showCouponFeedback('Preencha seus dados antes de reservar uma vaga THE100.', 'error');
    return;
  }
  const button = $('#applyCoupon');
  const input = $('#couponInput');
  const code = input?.value.trim().toUpperCase() || '';
  if (!code) {
    showCouponFeedback('Digite um cupom para aplicar.', 'error');
    return;
  }
  setBusy(button, true, 'Validando...');
  showCouponFeedback('Validando e reservando a vaga no backend...', 'info');
  try {
    const data = await api('/checkout/coupon/validate', {
      method: 'POST',
      body: JSON.stringify({ ...buyerPayload(), coupon: code })
    });
    activeCoupon = data.coupon || code;
    applyQuote(data);
    setText('#couponCodeLabel', activeCoupon);
    const priceText = moneyCents(Number(data.charged_monthly_price_cents));
    const remainingText = Number.isFinite(Number(data.remaining)) ? ` · ${data.remaining} vagas livres após reservas atuais` : '';
    setText('#couponDescription', `Preço fundador travado em ${priceText}/mês${remainingText}`);
    $('#couponApplied')?.classList.remove('hidden');
    if (data.campaign_state === 'FOUNDER_LOCKED') {
      showCouponFeedback(`Seu cadastro já possui o preço fundador de ${priceText}/mês.`, 'ok');
    } else if (data.campaign_state === 'PAYMENT_PENDING') {
      showCouponFeedback('THE100 já está reservado no checkout em andamento.', 'ok');
    } else {
      showCouponFeedback('Vaga THE100 reservada temporariamente. O benefício é confirmado após o pagamento aprovado.', 'ok');
    }
  } catch (error) {
    activeCoupon = '';
    pricingState.campaignState = 'IDLE';
    currentTotalCents = pricingState.normalCents;
    $('#couponApplied')?.classList.add('hidden');
    if (error.code === 'THE100_SOLD_OUT') {
      pricingState.remaining = 0;
      updateCampaignAvailability();
      showCouponFeedback('As 100 vagas da campanha The 100 foram preenchidas. Você pode continuar com a mensalidade normal.', 'error');
    } else if (error.code === 'THE100_RESERVATION_UNAVAILABLE') {
      showCouponFeedback('As vagas disponíveis estão temporariamente reservadas. Tente novamente em alguns minutos.', 'warning');
    } else {
      showCouponFeedback(error.message || 'Cupom inválido ou indisponível.', 'error');
    }
    updateSummary();
  } finally {
    setBusy(button, false);
  }
}

async function removeCoupon() {
  const previousCoupon = activeCoupon;
  activeCoupon = '';
  pricingState.campaignState = 'IDLE';
  currentTotalCents = pricingState.normalCents;
  if ($('#couponInput')) $('#couponInput').value = '';
  $('#couponApplied')?.classList.add('hidden');
  showCouponFeedback('Cupom removido.');
  updateSummary();
  updateCampaignAvailability();
  if (previousCoupon === 'THE100' && validateBuyer()) {
    try {
      const data = await api('/checkout/coupon/release', {
        method: 'POST',
        body: JSON.stringify(buyerPayload())
      });
      applyCampaignCounts(data);
      if (data.released) showCouponFeedback('Cupom removido e reserva temporária liberada.', 'ok');
    } catch (_) {
      // If the checkout is already payment-pending the backend intentionally keeps the claim.
    }
  }
}

async function startTrial() {
  if (!validateBuyer()) return;
  const button = $('#startTrial');
  setBusy(button, true, 'Preparando seu acesso...');
  try {
    const data = await api('/checkout/trial/request', {
      method: 'POST',
      body: JSON.stringify(buyerPayload())
    });
    if (data.public_token) localStorage.setItem('checkout_public_token', data.public_token);
    if (!data.eligible) {
      showModal(
        'Teste grátis já utilizado',
        data.message || 'Este cadastro já utilizou os 3 dias grátis. Para voltar ao Consenso, faça a assinatura mensal.',
        { label: 'Ir para pagamento', scrollTo: '#pagamento' }
      );
      return;
    }
    if (!data.telegram_url) throw new Error(data.message || 'Não foi possível conectar ao Telegram agora.');
    window.location.href = data.telegram_url;
  } catch (error) {
    showModal('Não foi possível iniciar o teste', error.message || 'Tente novamente em instantes.');
  } finally {
    setBusy(button, false);
  }
}

async function startPurchase() {
  if (!validateBuyer()) return;
  const button = $('#finishPurchase');
  setBusy(button, true, 'Abrindo Mercado Pago...');
  try {
    const data = await api('/checkout/purchase', {
      method: 'POST',
      body: JSON.stringify({ ...buyerPayload(), coupon: activeCoupon })
    });
    applyQuote(data);
    if (data.public_token) localStorage.setItem('checkout_public_token', data.public_token);
    if (data.telegram_connect_url) localStorage.setItem('checkout_telegram_connect_url', data.telegram_connect_url);
    if (data.telegram_link_key) localStorage.setItem('checkout_telegram_link_key', data.telegram_link_key);
    if (!data.checkout_url) throw new Error('O Mercado Pago não retornou o checkout da assinatura.');
    window.location.href = data.checkout_url;
  } catch (error) {
    if (error.code === 'THE100_SOLD_OUT' || error.code === 'THE100_RESERVATION_UNAVAILABLE') {
      activeCoupon = '';
      pricingState.campaignState = 'IDLE';
      currentTotalCents = pricingState.normalCents;
      if (error.code === 'THE100_SOLD_OUT') pricingState.remaining = 0;
      $('#couponApplied')?.classList.add('hidden');
      updateSummary();
      updateCampaignAvailability();
      const soldOut = error.code === 'THE100_SOLD_OUT';
      showModal(
        soldOut ? 'THE100 esgotado' : 'Vagas THE100 temporariamente reservadas',
        soldOut
          ? `As 100 vagas da campanha The 100 foram preenchidas. Você pode continuar com a mensalidade normal${pricingState.normalCents === null ? '' : ` de ${moneyCents(pricingState.normalCents)}/mês`}.`
          : 'As vagas disponíveis estão temporariamente reservadas por outros checkouts. Você pode tentar novamente depois ou continuar com o preço normal.',
        { label: 'Continuar no preço normal', scrollTo: '#pagamento' }
      );
    } else {
      showModal('Pagamento indisponível', error.message || 'Não foi possível abrir o Mercado Pago.');
    }
  } finally {
    setBusy(button, false);
  }
}

async function getFreshTelegramLink(publicToken) {
  const linkKey = localStorage.getItem('checkout_telegram_link_key') || '';
  if (!linkKey) return localStorage.getItem('checkout_telegram_connect_url') || '';
  try {
    const data = await api(`/checkout/telegram-link/${encodeURIComponent(publicToken)}`, {
      method: 'POST',
      headers: { 'X-Checkout-Link-Key': linkKey },
      body: '{}'
    });
    if (data.telegram_connect_url) {
      localStorage.setItem('checkout_telegram_connect_url', data.telegram_connect_url);
      return data.telegram_connect_url;
    }
  } catch (_) {
    // The stored link may still be valid; fall back to it below.
  }
  return localStorage.getItem('checkout_telegram_connect_url') || '';
}

async function handlePaymentReturn() {
  const params = new URLSearchParams(window.location.search);
  if (params.get('payment') !== 'return') return;
  const publicToken = localStorage.getItem('checkout_public_token') || '';
  if (!publicToken) {
    showModal('Retorno do Mercado Pago', 'Seu pagamento está sendo processado. Se precisar vincular o Telegram, volte ao checkout usando o mesmo cadastro.');
    return;
  }
  let status = null;
  try {
    status = await api(`/checkout/status/${encodeURIComponent(publicToken)}`, { method: 'GET' });
  } catch (_) {
    status = null;
  }
  const telegramUrl = await getFreshTelegramLink(publicToken);
  const approved = status?.access_kind === 'paid' && status?.access_status === 'active';
  const linked = Boolean(status?.telegram_linked);
  if (approved && linked) {
    showModal('Pagamento confirmado', 'Seu acesso pago está ativo. O bot enviará o convite do Consenso para a conta do Telegram vinculada.');
    return;
  }
  if (telegramUrl) {
    showModal(
      approved ? 'Pagamento confirmado' : 'Pagamento em confirmação',
      approved
        ? 'Pagamento aprovado. Vincule agora seu Telegram para receber o acesso ao Consenso.'
        : 'Vincule seu Telegram agora. Assim que o Mercado Pago confirmar a cobrança, o bot libera o Consenso automaticamente.',
      { label: 'Vincular Telegram', url: telegramUrl }
    );
    return;
  }
  showModal(
    approved ? 'Pagamento confirmado' : 'Pagamento em confirmação',
    approved
      ? 'Seu pagamento foi aprovado. Se o acesso não aparecer no Telegram, volte ao checkout usando o mesmo cadastro.'
      : 'O Mercado Pago ainda está confirmando a cobrança. Seu acesso será atualizado automaticamente.'
  );
}

function openFeedback() {
  const email = $('#email')?.value.trim() || '';
  if (email && $('#feedbackEmail') && !$('#feedbackEmail').value) $('#feedbackEmail').value = email;
  setText('#feedbackStatus', '');
  $('#feedbackStatus')?.classList.remove('ok', 'error');
  $('#feedbackModal')?.classList.remove('hidden');
  $('#feedbackMessage')?.focus();
}

function closeFeedback() {
  $('#feedbackModal')?.classList.add('hidden');
}

async function submitFeedback(event) {
  event.preventDefault();
  const message = $('#feedbackMessage')?.value.trim() || '';
  const status = $('#feedbackStatus');
  if (!message) {
    if (status) {
      status.textContent = 'Escreva uma mensagem antes de enviar.';
      status.className = 'feedback-status error';
    }
    $('#feedbackMessage')?.focus();
    return;
  }
  const button = $('#sendFeedback');
  setBusy(button, true, 'Enviando...');
  try {
    await api('/public/feedback', {
      method: 'POST',
      body: JSON.stringify({
        rating: $('#feedbackRating')?.value || '',
        category: $('#feedbackCategory')?.value || '',
        message,
        email: $('#feedbackEmail')?.value.trim() || '',
        website: $('#feedbackWebsite')?.value || ''
      })
    });
    if (status) {
      status.textContent = 'Feedback recebido. Obrigado por ajudar a melhorar o GolScope.';
      status.className = 'feedback-status ok';
    }
    $('#feedbackForm')?.reset();
  } catch (error) {
    if (status) {
      status.textContent = error.message || 'Não foi possível enviar o feedback agora.';
      status.className = 'feedback-status error';
    }
  } finally {
    setBusy(button, false);
  }
}

$('#startTrial')?.addEventListener('click', startTrial);
$('#applyCoupon')?.addEventListener('click', applyCoupon);
$('#couponInput')?.addEventListener('keydown', (event) => {
  if (event.key === 'Enter') applyCoupon();
});
$('#removeCoupon')?.addEventListener('click', removeCoupon);
$('#finishPurchase')?.addEventListener('click', startPurchase);

$('#openFeedback')?.addEventListener('click', openFeedback);
$('#closeFeedback')?.addEventListener('click', closeFeedback);
$('#feedbackForm')?.addEventListener('submit', submitFeedback);
$('#feedbackModal')?.addEventListener('click', (event) => {
  if (event.target.id === 'feedbackModal') closeFeedback();
});

document.querySelectorAll('.step').forEach((button) => {
  button.addEventListener('click', () => {
    const target = document.querySelector(`#${button.dataset.stepTarget}`);
    if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    document.querySelectorAll('.step').forEach((item) => item.classList.toggle('active', item === button));
  });
});

$('#closeModal')?.addEventListener('click', closeModal);
$('#modalOk')?.addEventListener('click', () => {
  const action = modalAction;
  closeModal();
  if (!action) return;
  if (action.url) {
    window.location.href = action.url;
    return;
  }
  if (action.scrollTo) document.querySelector(action.scrollTo)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
});
$('#modal')?.addEventListener('click', (event) => {
  if (event.target.id === 'modal') closeModal();
});

installInputMasks();
updateSummary();
loadPricing();
handlePaymentReturn();
