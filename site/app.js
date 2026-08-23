const CONFIG = {
  apiBase: 'https://ia-over-production.up.railway.app',
  productName: 'Grupo Premium',
  basePrice: 150,
  currency: 'BRL'
};

let activeCoupon = '';
let discountPercent = 0;
let currentTotal = CONFIG.basePrice;
let modalAction = null;

const $ = (selector) => document.querySelector(selector);
const money = (value) => new Intl.NumberFormat('pt-BR', {
  style: 'currency',
  currency: CONFIG.currency
}).format(Number(value || 0));

function buyerPayload() {
  return {
    name: $('#name').value.trim(),
    email: $('#email').value.trim(),
    phone: $('#phone').value.trim(),
    cpf: $('#cpf').value.trim()
  };
}

function validateBuyer() {
  const required = ['name', 'email', 'phone', 'cpf'];
  let firstInvalid = null;
  required.forEach((id) => {
    const input = $(`#${id}`);
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

function updateSummary() {
  const discount = Math.max(0, CONFIG.basePrice - currentTotal);
  $('#subtotal').textContent = money(CONFIG.basePrice);
  $('#total').textContent = money(currentTotal);
  const line = $('#discountLine');
  if (discount > 0) {
    line.classList.remove('hidden');
    $('#discountValue').textContent = `- ${money(discount)}`;
  } else {
    line.classList.add('hidden');
  }
}

function showCouponFeedback(message, type = '') {
  const el = $('#couponFeedback');
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
    throw new Error(data.error || data.message || 'Não foi possível concluir a operação.');
  }
  return data;
}

function showModal(title, text, action = null) {
  $('#modalTitle').textContent = title;
  $('#modalText').textContent = text;
  modalAction = action;
  const button = $('#modalOk');
  button.textContent = action?.label || 'Entendi';
  $('#modal').classList.remove('hidden');
}

function closeModal() {
  $('#modal').classList.add('hidden');
  modalAction = null;
  $('#modalOk').textContent = 'Entendi';
}

async function applyCoupon() {
  const button = $('#applyCoupon');
  const input = $('#couponInput');
  const code = input.value.trim().toUpperCase();
  if (!code) {
    showCouponFeedback('Digite um cupom para aplicar.', 'error');
    return;
  }
  setBusy(button, true, 'Validando...');
  try {
    const data = await api('/checkout/coupon/validate', {
      method: 'POST',
      body: JSON.stringify({ coupon: code })
    });
    activeCoupon = data.coupon || code;
    discountPercent = Number(data.discount_percent || 0);
    currentTotal = Number(data.amount || CONFIG.basePrice);
    $('#couponCodeLabel').textContent = activeCoupon;
    $('#couponDescription').textContent = `${discountPercent}% de desconto na mensalidade`;
    $('#couponApplied').classList.remove('hidden');
    showCouponFeedback('Cupom aplicado com sucesso.', 'ok');
    updateSummary();
  } catch (error) {
    activeCoupon = '';
    discountPercent = 0;
    currentTotal = CONFIG.basePrice;
    $('#couponApplied').classList.add('hidden');
    showCouponFeedback(error.message || 'Cupom inválido ou indisponível.', 'error');
    updateSummary();
  } finally {
    setBusy(button, false);
  }
}

function removeCoupon() {
  activeCoupon = '';
  discountPercent = 0;
  currentTotal = CONFIG.basePrice;
  $('#couponInput').value = '';
  $('#couponApplied').classList.add('hidden');
  showCouponFeedback('Cupom removido.');
  updateSummary();
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
    if (data.public_token) {
      localStorage.setItem('checkout_public_token', data.public_token);
    }
    if (!data.eligible) {
      showModal(
        'Teste grátis já utilizado',
        data.message || 'Este cadastro já utilizou os 3 dias grátis. Para voltar ao Consenso, faça a assinatura mensal.',
        { label: 'Ir para pagamento', scrollTo: '#pagamento' }
      );
      return;
    }
    if (!data.telegram_url) {
      throw new Error(data.message || 'Não foi possível conectar ao Telegram agora.');
    }
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
    if (data.public_token) {
      localStorage.setItem('checkout_public_token', data.public_token);
    }
    if (data.telegram_connect_url) {
      localStorage.setItem('checkout_telegram_connect_url', data.telegram_connect_url);
    }
    if (!data.checkout_url) {
      throw new Error('O Mercado Pago não retornou o checkout da assinatura.');
    }
    window.location.href = data.checkout_url;
  } catch (error) {
    showModal('Pagamento indisponível', error.message || 'Não foi possível abrir o Mercado Pago.');
  } finally {
    setBusy(button, false);
  }
}

async function getFreshTelegramLink(publicToken) {
  try {
    const data = await api(`/checkout/telegram-link/${encodeURIComponent(publicToken)}`, {
      method: 'POST',
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
    showModal(
      'Retorno do Mercado Pago',
      'Seu pagamento está sendo processado. Se precisar vincular o Telegram, volte ao checkout usando o mesmo cadastro.'
    );
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
    showModal(
      'Pagamento confirmado',
      'Seu acesso pago está ativo. O bot enviará o convite do Consenso para a conta do Telegram vinculada.'
    );
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

$('#startTrial').addEventListener('click', startTrial);
$('#applyCoupon').addEventListener('click', applyCoupon);
$('#couponInput').addEventListener('keydown', (event) => {
  if (event.key === 'Enter') applyCoupon();
});
$('#removeCoupon').addEventListener('click', removeCoupon);
$('#finishPurchase').addEventListener('click', startPurchase);

document.querySelectorAll('.step').forEach((button) => {
  button.addEventListener('click', () => {
    const target = document.querySelector(`#${button.dataset.stepTarget}`);
    if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    document.querySelectorAll('.step').forEach((item) => item.classList.toggle('active', item === button));
  });
});

$('#closeModal').addEventListener('click', closeModal);
$('#modalOk').addEventListener('click', () => {
  const action = modalAction;
  closeModal();
  if (!action) return;
  if (action.url) {
    window.location.href = action.url;
    return;
  }
  if (action.scrollTo) {
    document.querySelector(action.scrollTo)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
});
$('#modal').addEventListener('click', (event) => {
  if (event.target.id === 'modal') closeModal();
});

updateSummary();
handlePaymentReturn();
