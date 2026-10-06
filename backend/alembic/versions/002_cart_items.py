from alembic import op
import sqlalchemy as sa

revision = "002_cart_items"
down_revision = "001_init"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "cart_items",
        sa.Column("id", sa.Integer(), primary_key=True, comment="主键"),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False, comment="用户 ID"),
        sa.Column("dish_id", sa.Integer(), sa.ForeignKey("dishes.id"), nullable=False, comment="菜品 ID"),
        sa.Column("qty", sa.Integer(), nullable=False, comment="数量"),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, comment="最近修改时间"),
        sa.UniqueConstraint("user_id", "dish_id", name="uk_cart_user_dish"),
        comment="购物车：同一用户同一道菜只有一行",
    )
    op.create_index("ix_cart_items_user_id", "cart_items", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_cart_items_user_id", table_name="cart_items")
    op.drop_table("cart_items")
