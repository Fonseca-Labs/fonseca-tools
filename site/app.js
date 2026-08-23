const CONFIG = {
  productName: 'Grupo Premium',
  basePrice: 150,
  trialDays: 3,
  currency: 'BRL',
  coupons: {
    FONSECA5: { type: 'percent', value: 5, label: '5% de desconto na mensalidade' }
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
  return coupon ? CONFIG.basePrice * (coupon.value / 100) : 0;
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
  if (!code) return showCouponFeedback('Digite um cupom para aplicar.', 'error');
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

function showModal(title, text) {
  document.querySelector('#modalTitle').textContent = title;
  document.querySelector('#modalText').textContent = text;
  document.querySelector('#modal').classList.remove('hidden');
}

function closeModal() {
  document.querySelector('#modal').classList.add('hidden');
}

document.querySelector('#startTrial').addEventListener('click', () => {
  if (!validateBuyer()) return;
  showModal(
    'Teste grátis de 3 dias',
    'A tela já está pronta para o fluxo de trial. Falta conectar o backend ao Telegram para validar se este CPF/Telegram já usou o teste, registrar as 72 horas e gerar o acesso individual ao grupo.'
  );
});

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
    document.querySelector(`#${button.dataset.stepTarget}`).scrollIntoView({ behavior: 'smooth', block: 'start' });
    document.querySelectorAll('.step').forEach((b) => b.classList.toggle('active', b === button));
  });
});

document.querySelector('#finishPurchase').addEventListener('click', () => {
  if (!validateBuyer()) return;
  const total = Math.max(0, CONFIG.basePrice - getDiscount());
  showModal(
    'Pagamento de 30 dias',
    `A página está preparada para criar a assinatura de ${money(total)} no Mercado Pago. Assim que o backend público for conectado, este botão abrirá o checkout seguro do Mercado Pago.`
  );
});

document.querySelector('#closeModal').addEventListener('click', closeModal);
document.querySelector('#modalOk').addEventListener('click', closeModal);
document.querySelector('#modal').addEventListener('click', (e) => {
  if (e.target.id === 'modal') closeModal();
});

updateSummary();
