# 点餐 Diancan

前后端分离的点餐项目。你只会 Java 的话，把 FastAPI 当 Spring Boot、把 SQLAlchemy 当 JPA 即可。

## 技术栈

- 顾客端：uni-app（先跑 App / H5）
- 商家后台：Vue 3 + Element Plus
- 后端：FastAPI
- MySQL + Redis + JWT
- SQLAlchemy 2 + Alembic

## 演示账号

| 角色 | 用户名 | 密码 |
|---|---|---|
| 店员 | admin | admin123 |
| 顾客 | user | user123 |

## 启动

本机先自行启动 **MySQL**（3306）和 **Redis**（6379），账号密码写在项目根目录 `.env`。没有 `.env` 时：`copy .env.example .env`。

### 1. 后端（在 `backend` 目录）

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload --port 8000
```

接口文档：http://127.0.0.1:8000/docs

### 2. 商家后台（在 `admin` 目录）

```bash
npm install
npm run dev
```

打开 http://127.0.0.1:5173

### 3. 顾客端 uni-app（在 `app` 目录）

- 推荐：用 **HBuilderX** 打开 `app` 目录，运行到手机或模拟器。
- 真机把项目根目录 `.env` 的 `VITE_API_BASE` 改成电脑局域网 IP，如 `http://192.168.1.8:8000`
- 本机 H5：`npm install` 后 `npm run dev:h5`（走代理，不必改 BASE_URL）

## 目录

```
backend/     FastAPI
admin/        商家后台
app/          uni-app 顾客端
LEARNING.md   学习任务说明
```
