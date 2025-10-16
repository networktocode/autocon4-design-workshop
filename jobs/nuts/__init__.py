"""Module to run NUTS tests from Nautobot."""

import io
import json
import sys
from pathlib import Path

import pytest
from jinja2 import Environment, FileSystemLoader

from nautobot.apps.jobs import Job, ObjectVar, register_jobs
from nautobot.dcim.models import Interface
from nautobot.extras.models import Role
from nautobot.ipam.models import IPAddress

from containerlab.models import Topology

name = "AUTOCON4"  # pylint: disable=invalid-name


def generate_test_file(
    template_filename: str, output_filename: str, topology: Topology, **kwargs
):
    """Generate a test file from a Jinja2 template."""
    pwd = Path(__file__).parent
    template_path = pwd / "templates"
    env = Environment(
        loader=FileSystemLoader(template_path),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template(template_filename)
    output = template.render(topology=topology, **kwargs)
    output_path = pwd / output_filename
    if output_path.exists():
        output_path.unlink()
    output_path.write_text(output)


class NutJob(Job):
    """A job to run NUTS tests."""

    topology = ObjectVar(
        description="The topology to use for the tests.",
        model=Topology,
        required=True,
    )

    class Meta:
        """Metadata for the NutJob."""

        name = "NUTS Tests"
        description = "A job to run NUTS tests."
        has_sensitive_variables = False

    def generate_test_files(self, topology: Topology):
        """Generate NUTS tests from the topology."""

        # Get devices from the topology
        devices = topology.dynamic_group.members.all()
        if not devices:
            self.logger.error("No devices found in the topology.")
            return {}
        nodes = [device.name for device in devices]

        generate_test_file(
            template_filename="hosts.yaml.j2",
            output_filename="/source/inventory/hosts.yaml",
            topology=topology,
            nodes=nodes,
        )

        generate_test_file(
            template_filename="test_lldp_adj.yaml.j2",
            output_filename="tests/test_lldp_adj.yaml",
            topology=topology,
            nodes=nodes,
        )

        generate_test_file(
            template_filename="test_ospf_adj.yaml.j2",
            output_filename="tests/test_ospf_adj.yaml",
            topology=topology,
            nodes=nodes,
        )

        device_peers = []
        role = Role.objects.get(name="Branch:L3Link")
        for device in devices:
            for interface in Interface.objects.filter(device=device, role=role):
                device_peers.append(
                    (
                        device.name,
                        interface.ip_addresses.first().siblings().first().host,
                    )
                )
        generate_test_file(
            template_filename="test_ping_connected.yaml.j2",
            output_filename="tests/test_ping_connected.yaml",
            topology=topology,
            device_peers=device_peers,
        )

        device_remoteloopbacks = []
        role = Role.objects.get(name="Branch:Loopback")
        for device in devices:
            loopback_interface = Interface.objects.get(device=device, role=role)
            remoteloopbacks = [
                rl.host for rl in loopback_interface.ip_addresses.first().siblings()
            ]
            device_remoteloopbacks.append((device.name, remoteloopbacks))
        generate_test_file(
            template_filename="test_ping_loopbacks.yaml.j2",
            output_filename="tests/test_ping_loopbacks.yaml",
            topology=topology,
            device_remoteloopbacks=device_remoteloopbacks,
        )

    def run(self, topology: Topology):  # pylint: disable=arguments-differ
        """Run NUTS tests."""

        # Construct the tests
        self.generate_test_files(topology)

        self.logger.info("Running NUTS tests...")

        # Set up the paths
        pwd = Path(__file__).parent
        tests_path = pwd / "tests"
        report_path = pwd / ".report.json"
        if report_path.exists():
            report_path.unlink()

        # Temporarily disable stdout and stderr to avoid cluttering the Nautobot logs
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()

        try:
            # Run the tests
            pytest.main(
                [
                    tests_path,
                    "-p",
                    "no:all",
                    "--json-report",
                    f"--json-report-file={report_path}",
                ]
            )
        finally:
            # Restore stdout and stderr
            sys.stdout = original_stdout
            sys.stderr = original_stderr

        # Read the result, return the report
        if report_path.exists():
            report_data = report_path.read_text()
            self.create_file("nuts_report.json", report_data)
            full_report = json.loads(report_data)
            report = {
                "created": full_report.get("created"),
                "duration": full_report.get("duration"),
                "exitcode": full_report.get("exitcode"),
                "summary": full_report.get("summary"),
                "result": {},
            }
            for result in ["error", "failed", "passed"]:
                report["result"][result] = [
                    test.get("nodeid")
                    for test in full_report.get("tests")
                    if test.get("outcome") == result
                ]
            return report
        self.logger.error("Report was not generated!")
        return {}


register_jobs(NutJob)
