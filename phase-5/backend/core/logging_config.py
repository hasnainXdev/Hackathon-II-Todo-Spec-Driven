import logging
import sys
from pathlib import Path

# Create logs directory if it doesn't exist
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(logs_dir / "app.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

# Create logger instances for different modules
logger = logging.getLogger(__name__)
api_logger = logging.getLogger("api")
auth_logger = logging.getLogger("auth")
db_logger = logging.getLogger("database")
task_logger = logging.getLogger("task")