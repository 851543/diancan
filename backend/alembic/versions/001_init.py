from alembic import op
import sqlalchemy as sa

revision = "001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, comment="主键"),
        sa.Column("username", sa.String(64), nullable=False, comment="登录用户名"),
        sa.Column("hashed_password", sa.String(255), nullable=False, comment="密码哈希，不存明文"),
        sa.Column("role", sa.String(16), nullable=False, comment="角色：customer 顾客 / admin 店员"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, comment="注册时间"),
        comment="用户账号",
    )
    op.create_index("ix_users_username", "users", ["username"], unique=True)

    op.create_table(
        "dishes",
        sa.Column("id", sa.Integer(), primary_key=True, comment="主键"),
        sa.Column("name", sa.String(128), nullable=False, comment="菜名"),
        sa.Column("category", sa.String(64), nullable=False, comment="分类，如热菜/素菜"),
        sa.Column("description", sa.Text(), nullable=False, comment="简介"),
        sa.Column("price_cents", sa.Integer(), nullable=False, comment="单价，单位分"),
        sa.Column("image_url", sa.String(512), nullable=False, comment="图片地址"),
        sa.Column("is_on", sa.Integer(), nullable=False, comment="是否上架：1 上架，0 下架"),
        comment="菜品菜单",
    )
    op.create_index("ix_dishes_category", "dishes", ["category"])

    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), primary_key=True, comment="主键/单号"),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False, comment="下单用户 ID"),
        sa.Column(
            "status",
            sa.String(32),
            nullable=False,
            comment="状态：pending/paid/preparing/ready/completed/cancelled",
        ),
        sa.Column("total_cents", sa.Integer(), nullable=False, comment="订单总价，单位分"),
        sa.Column("remark", sa.String(255), nullable=False, comment="顾客备注"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, comment="下单时间"),
        comment="订单主表",
    )
    op.create_index("ix_orders_status", "orders", ["status"])

    op.create_table(
        "order_items",
        sa.Column("id", sa.Integer(), primary_key=True, comment="主键"),
        sa.Column("order_id", sa.Integer(), sa.ForeignKey("orders.id"), nullable=False, comment="所属订单 ID"),
        sa.Column("dish_id", sa.Integer(), sa.ForeignKey("dishes.id"), nullable=False, comment="原菜品 ID"),
        sa.Column("name", sa.String(128), nullable=False, comment="下单时菜名快照"),
        sa.Column("price_cents", sa.Integer(), nullable=False, comment="下单时单价快照，单位分"),
        sa.Column("qty", sa.Integer(), nullable=False, comment="数量"),
        comment="订单明细（锁价快照，改菜单不影响历史单）",
    )


def downgrade() -> None:
    op.drop_table("order_items")
    op.drop_table("orders")
    op.drop_table("dishes")
    op.drop_table("users")
