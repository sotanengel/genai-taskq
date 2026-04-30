from genai_taskq.storage.db import Base, engine
from genai_taskq.storage import tables  # noqa: F401


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
