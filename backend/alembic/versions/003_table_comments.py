"""为已存在的表补 MySQL COMMENT（新建库走 001/002 即可）。

主键 id 被外键引用，不能用 ALTER MODIFY，表注释 + 非主键列即可。
"""

from alembic import op
import sqlalchemy as sa

revision = "003_table_comments"
down_revision = "002_cart_items"
branch_labels = None
depends_on = None


def _col(table: str, name: str, type_, comment: str, nullable: bool = False) -> None:
    op.alter_column(
        table,
        name,
        existing_type=type_,
        existing_nullable=nullable,
        comment=comment,
        existing_comment=None,
    )


def upgrade() -> None:
    op.execute("SET NAMES utf8mb4")

    op.execute("ALTER TABLE users COMMENT='用户账号'")
    _col("users", "username", sa.String(64), "登录用户名")
    _col("users", "hashed_password", sa.String(255), "密码哈希，不存明文")
    _col("users", "role", sa.String(16), "角色：customer 顾客 / admin 店员")
    _col("users", "created_at", sa.DateTime(timezone=True), "注册时间")

    op.execute("ALTER TABLE dishes COMMENT='菜品菜单'")
    _col("dishes", "name", sa.String(128), "菜名")
    _col("dishes", "category", sa.String(64), "分类，如热菜/素菜")
    _col("dishes", "description", sa.Text(), "简介")
    _col("dishes", "price_cents", sa.Integer(), "单价，单位分")
    _col("dishes", "image_url", sa.String(512), "图片地址")
    _col("dishes", "is_on", sa.Integer(), "是否上架：1 上架，0 下架")

    op.execute("ALTER TABLE orders COMMENT='订单主表'")
    _col("orders", "user_id", sa.Integer(), "下单用户 ID")
    _col(
        "orders",
        "status",
        sa.String(32),
        "状态：pending/paid/preparing/ready/completed/cancelled",
    )
    _col("orders", "total_cents", sa.Integer(), "订单总价，单位分")
    _col("orders", "remark", sa.String(255), "顾客备注")
    _col("orders", "created_at", sa.DateTime(timezone=True), "下单时间")

    op.execute("ALTER TABLE order_items COMMENT='订单明细（锁价快照，改菜单不影响历史单）'")
    _col("order_items", "order_id", sa.Integer(), "所属订单 ID")
    _col("order_items", "dish_id", sa.Integer(), "原菜品 ID")
    _col("order_items", "name", sa.String(128), "下单时菜名快照")
    _col("order_items", "price_cents", sa.Integer(), "下单时单价快照，单位分")
    _col("order_items", "qty", sa.Integer(), "数量")

    op.execute("ALTER TABLE cart_items COMMENT='购物车：同一用户同一道菜只有一行'")
    _col("cart_items", "user_id", sa.Integer(), "用户 ID")
    _col("cart_items", "dish_id", sa.Integer(), "菜品 ID")
    _col("cart_items", "qty", sa.Integer(), "数量")
    _col("cart_items", "updated_at", sa.DateTime(timezone=True), "最近修改时间")


def downgrade() -> None:
    pass
