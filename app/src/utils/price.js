/** 金额用「分」存储，展示时转成元。 */

export function yuan(cents) {
  const n = Number(cents);
  if (!Number.isFinite(n)) return "0.00";
  return (n / 100).toFixed(2);
}

export function cartTotal(items) {
  if (!items || !items.length) return 0;
  return items.reduce((sum, i) => sum + (i.price_cents || 0) * (i.qty || 0), 0);
}
