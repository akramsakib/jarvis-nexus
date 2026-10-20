from __future__ import annotations
import uvicorn
from nexus_core.config import settings

def main():
    uvicorn.run("nexus.api:app", host=settings.host, port=settings.port, reload=False)

if __name__ == "__main__":
    main()
