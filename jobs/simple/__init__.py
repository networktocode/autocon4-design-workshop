"""Basic design demonstrates the capabilities of the Design Builder."""

from nautobot.apps.jobs import register_jobs, StringVar

from nautobot_design_builder.design_job import DesignJob

from .context import SimpleDesignContext

name = "AUTOCON4"


class SimpleDesign(DesignJob):
    """A simple design to learn."""

    class Meta:
        """Metadata for the SimpleDesign."""

        name = "Simple Design"
        description = "A simple design."
        nautobot_version = ">=2"
        has_sensitive_variables = False
        design_file = "designs/0000_simpledesign.yaml.j2"
        context_class = SimpleDesignContext

    manufacturer = StringVar(label="New manufacturer name")


register_jobs(SimpleDesign)
