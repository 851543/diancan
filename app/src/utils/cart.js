import { request } from "./api";

export function fetchCart() {
  return request("/cart", "GET");
}

export function addCartItem(dishId, qty = 1) {
  return request("/cart", "POST", { dish_id: dishId, qty });
}

export function clearCart() {
  return request("/cart", "DELETE");
}
