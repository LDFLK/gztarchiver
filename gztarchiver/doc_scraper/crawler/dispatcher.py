from gztarchiver.doc_scraper.v1 import run_v1_pipeline
from gztarchiver.doc_scraper.v2 import run_v2_pipeline

PIPELINES = {
    "v1": run_v1_pipeline,
    "v2": run_v2_pipeline,
}

DEFAULT_VERSION = "v2"

def get_crawler_pipeline(version=None):
    """Retrieve crawler pipeline corresponding to the given version string."""
    selected_version = (version or DEFAULT_VERSION).lower()
    if selected_version not in PIPELINES:
        raise ValueError(
            f"Unsupported crawler version '{selected_version}'. Supported versions: {list(PIPELINES.keys())}"
        )
    return PIPELINES[selected_version], selected_version
