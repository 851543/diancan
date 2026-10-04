# 学习任务（已完成）

1. 认证 `verify_password`：用 passlib 校验 bcrypt。
2. 菜单筛选 `_filter_dishes`：keyword 模糊、category 精确。
3. 订单状态机 `can_transition`：按 `ALLOWED_FROM` 判断能否流转。
4. 购物车：MySQL 表 `cart_items` 落库，Redis Hash（`HINCRBY` / `HGETALL`）加速。接口 `GET/POST/DELETE /cart`。
5. 商家后台概览 `summarizeOrders`：订单数、待处理、已完成营业额。
6. 顾客端金额 `yuan` / `cartTotal`：分转元、购物车合计。
