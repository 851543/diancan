# 点餐 Diancan

前后端分离的点餐系统：顾客点餐下单，店员管菜单和订单。

## 技术栈

- 顾客端：uni-app（App / H5）
- 商家后台：Vue 3 + Element Plus
- 后端：FastAPI
- MySQL + Redis + JWT
- SQLAlchemy 2 + Alembic

## 配置

项目根目录复制 `.env.example` 为 `.env`，至少改这些：

- `JWT_SECRET`：随机长密钥，不要用示例值
- `MYSQL_*` / `REDIS_*`：真实库和缓存
- `CORS_ORIGINS`：后台、H5 的实际域名（同域反代可留空）
- `ADMIN_USERNAME` / `ADMIN_PASSWORD`：只在创建首个店员时用
- `VITE_API_BASE`：打包后台或真机顾客端时的 API 地址
- `APP_ENV=production` 时关闭 `/docs`，并拒绝默认 JWT 密钥

顾客自行注册；菜单由店员在后台添加，不再写入演示数据。

## 启动

先启动 **MySQL**、**Redis**，并准备好 `.env`。

### 1. 后端（`backend` 目录）

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
python -m app.seed
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

`python -m app.seed` 只在库里还没有店员时，用 `.env` 的 `ADMIN_*` 创建账号。

### 2. 商家后台（`admin` 目录）

开发：`npm install` 后 `npm run dev`（http://127.0.0.1:5173）。

上线：改好 `VITE_API_BASE` 后 `npm run build`，把 `dist` 交给 Nginx。

### 3. 顾客端（`app` 目录）

- HBuilderX 打开 `app` 目录，发行到 App 或 H5。
- 真机把 `VITE_API_BASE` 改成可访问的 API 地址。

## 目录

```
backend/     FastAPI
  app/main.py      启动入口
  app/core/        配置、JWT、登录依赖
  app/db/          MySQL、Redis
  app/models/      表实体
  app/schemas/     接口 DTO
  app/routers/     HTTP 接口
  app/services/    业务逻辑
admin/        商家后台
app/          uni-app 顾客端
```
