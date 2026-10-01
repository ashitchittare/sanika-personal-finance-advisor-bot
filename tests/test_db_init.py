import os
import shutil
import tempfile
from pathlib import Path
from flask import Flask
from app.config import Config
from app import create_app
from app.extensions import db
from app.models.user import User


def test_clean_database_initialization_on_missing_directory():
    """
    Test that the application starts cleanly when instance directory does not exist,
    creates the directory automatically, and creates all SQLite tables without error.
    """
    temp_dir = tempfile.mkdtemp()
    temp_instance = Path(temp_dir) / "nested_instance_dir"
    db_file = temp_instance / "fresh_test.db"

    # Verify directory does NOT exist beforehand
    assert not temp_instance.exists()
    assert not db_file.exists()

    class FreshConfig(Config):
        TESTING = True
        DEBUG = True
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_file.resolve().as_posix()}"

    # Initialize app manually using custom fresh config
    app = Flask(__name__, instance_path=str(temp_instance))
    app.config.from_object(FreshConfig)

    # Ensure instance directory is created dynamically
    os.makedirs(app.instance_path, exist_ok=True)
    db.init_app(app)

    with app.app_context():
        import app.models
        db.create_all()

        # Insert a record to verify write access
        user = User(name="Sanika Fresh", email="sanika.fresh@example.com")
        user.set_password("SecurePass123")
        db.session.add(user)
        db.session.commit()

        # Query back
        fetched = User.query.filter_by(email="sanika.fresh@example.com").first()
        assert fetched is not None
        assert fetched.name == "Sanika Fresh"
        assert fetched.check_password("SecurePass123")

    # Verify physical file existence
    assert temp_instance.exists()
    assert db_file.exists()

    # Clean up
    shutil.rmtree(temp_dir, ignore_errors=True)
