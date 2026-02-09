# continuum/orchestrator/controller/controller_rewrite.py

from continuum.aira.meta_rewrite import meta_rewrite_llm


def initialize_legacy_rewrite_wrapper(controller):
    """
    Phase‑5 compatibility layer:
    Exposes the deprecated meta_rewrite_llm for UI tools,
    but keeps it out of the main controller logic.
    """

    def _legacy_meta_rewrite_llm(**kwargs):
        return meta_rewrite_llm(controller, **kwargs)

    controller.meta_rewrite_llm = _legacy_meta_rewrite_llm