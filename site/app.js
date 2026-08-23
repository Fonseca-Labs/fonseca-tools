const CONFIG = {
  productName: 'Acesso Premium',
  basePrice: 297,
  currency: 'BRL',
  coupons: {
    BEMVINDO10: { type: 'percent', value: 10, label: '10% de desconto' },
    VIP50: { type: 'fixed', value: 50, label: 'R$ 50 de desconto' },
    PREMIUM15: { type: 'percent', value: 15, label: '15% de desconto' }
  }
};

let activeCoupon = null;
let paymentMethod = 'pix';

const money = (value) => new Intl.NumberFormat('pt-BR', {
  style: 'currency',
  currency: CONFIG.currency
}).format(value);

function getDiscount() {
  if (!activeCoupon) return 0;
  const coupon = CONFIG.coupons[activeCoupon];
  if (!coupon) return 0;
  if (coupon.type === 'percent') return CONFIG.basePrice * (coupon.value / 100);
  return Math.min(coupon.value, CONFIG.basePrice);
}

function updateSummary() {
  const discount = getDiscount();
  const total = Math.max(0, CONFIG.basePrice - discount);

  document.querySelector('#subtotal').textContent = money(CONFIG.basePrice);
  document.querySelector('#total').textContent = money(total);

  const line = document.querySelector('#discountLine');
  if (discount > 0) {
    line.classList.remove('hidden');
    document.querySelector('#discountValue').textContent = `- ${money(discount)}`;
  } else {
    line.classList.add('hidden');
  }
}

function showCouponFeedback(message, type = '') {
  const el = document.querySelector('#couponFeedback');
  el.textContent = message;
  el.className = `coupon-feedback ${type}`;
}

function applyCoupon() {
  const input = document.querySelector('#couponInput');
  const code = input.value.trim().toUpperCase();
  const coupon = CONFIG.coupons[code];

  if (!code) {
    showCouponFeedback('Digite um cupom para aplicar.', 'error');
    return;
  }

  if (!coupon) {
    activeCoupon = null;
    document.querySelector('#couponApplied').classList.add('hidden');
    showCouponFeedback('Cupom inválido ou indisponível.', 'error');
    updateSummary();
    return;
  }

  activeCoupon = code;
  document.querySelector('#couponCodeLabel').textContent = code;
  document.querySelector('#couponDescription').textContent = coupon.label;
  document.querySelector('#couponApplied').classList.remove('hidden');
  showCouponFeedback('Cupom aplicado com sucesso.', 'ok');
  updateSummary();
}

function removeCoupon() {
  activeCoupon = null;
  document.querySelector('#couponInput').value = '';
  document.querySelector('#couponApplied').classList.add('hidden');
  showCouponFeedback('Cupom removido.');
  updateSummary();
}

function validateBuyer() {
  const required = ['name', 'email', 'phone', 'cpf'];
  let firstInvalid = null;
  required.forEach((id) => {
    const input = document.querySelector(`#${id}`);
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

function openModal() {
  const discount = getDiscount();
  const total = Math.max(0, CONFIG.basePrice - discount);
  document.querySelector('#modalText').textContent =
    `Checkout pronto para cobrar ${money(total)} via ${paymentMethod === 'pix' ? 'Pix' : 'cartão'}. A cobrança real entra assim que conectarmos o provedor de pagamento.`;
  document.querySelector('#modal').classList.remove('hidden');
}

function closeModal() {
  document.querySelector('#modal').classList.add('hidden');
}

document.querySelector('#applyCoupon').addEventListener('click', applyCoupon);
document.querySelector('#couponInput').addEventListener('keydown', (e) => {
  if (e.key === 'Enter') applyCoupon();
});
document.querySelector('#removeCoupon').addEventListener('click', removeCoupon);

document.querySelectorAll('.payment-tab').forEach((button) => {
  button.addEventListener('click', () => {
    paymentMethod = button.dataset.payment;
    document.querySelectorAll('.payment-tab').forEach((b) => b.classList.toggle('active', b === button));
    document.querySelectorAll('.payment-content').forEach((content) => content.classList.remove('active'));
    document.querySelector(`#payment-${paymentMethod}`).classList.add('active');
  });
});

document.querySelectorAll('.step').forEach((button) => {
  button.addEventListener('click', () => {
    const target = document.querySelector(`#${button.dataset.stepTarget}`);
    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    document.querySelectorAll('.step').forEach((b) => b.classList.toggle('active', b === button));
  });
});

document.querySelector('#finishPurchase').addEventListener('click', () => {
  if (!validateBuyer()) return;
  openModal();
});

document.querySelector('#closeModal').addEventListener('click', closeModal);
document.querySelector('#modalOk').addEventListener('click', closeModal);
document.querySelector('#modal').addEventListener('click', (e) => {
  if (e.target.id === 'modal') closeModal();
});

updateSummary();
