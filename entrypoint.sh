. venv/bin/activate
pip install alembic
alembic init -t async alembic
alembic revision -m "create accounts table"
alembic revision --autogenerate -m "Create products table"
alembic upgrade head 