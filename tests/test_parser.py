import pytest
from vnfm.parser.parser import ToscaParser
from vnfm.common.exceptions import VnfdValidationError


class TestToscaParser:
    def test_parse_yaml_valid(self):
        yaml_content = """
tosca_definitions_version: tosca_simple_yaml_1_2

description: A sample VNF

topology_template:
  node_templates:
    VDU1:
      type: tosca.nodes.nfv.Vdu.Compute
      properties:
        name: vdu1
  inputs:
    flavor:
      type: string
"""
        parser = ToscaParser()
        result = parser.parse_yaml(yaml_content)
        assert "nodes" in result
        assert "VDU1" in result["nodes"]
        assert result["nodes"]["VDU1"]["type"] == "tosca.nodes.nfv.Vdu.Compute"
        assert "inputs" in result
        assert "flavor" in result["inputs"]

    def test_parse_yaml_invalid(self):
        yaml_content = "invalid: tosca: data"
        parser = ToscaParser()
        with pytest.raises(VnfdValidationError):
            parser.parse_yaml(yaml_content)

    def test_parse_yaml_empty_topology(self):
        yaml_content = """
tosca_definitions_version: tosca_simple_yaml_1_2
"""
        parser = ToscaParser()
        with pytest.raises(VnfdValidationError):
            parser.parse_yaml(yaml_content)
