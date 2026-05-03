import yaml
from typing import Dict, Any, Optional
from toscaparser.tosca_template import ToscaTemplate
from toscaparser.common.exception import TOSCAException

from vnfm.common.exceptions import VnfdValidationError


class ToscaParser:
    def parse_csar(self, csar_path: str) -> Dict[str, Any]:
        try:
            tosca = ToscaTemplate(csar_path)
            return self._extract_vnfd(tosca)
        except TOSCAException as e:
            raise VnfdValidationError(f"TOSCA parse error: {e}")
        except Exception as e:
            raise VnfdValidationError(f"Unexpected parse error: {e}")

    def parse_yaml(self, yaml_content: str) -> Dict[str, Any]:
        try:
            tosca = ToscaTemplate(None, yaml_content, False, False)
            return self._extract_vnfd(tosca)
        except TOSCAException as e:
            raise VnfdValidationError(f"TOSCA parse error: {e}")
        except Exception as e:
            raise VnfdValidationError(f"Unexpected parse error: {e}")

    def _extract_vnfd(self, tosca: ToscaTemplate) -> Dict[str, Any]:
        topology = tosca.topology_template
        if not topology:
            raise VnfdValidationError("Missing topology_template in TOSCA")

        nodes = {}
        policies = []

        if topology.node_templates:
            for name, node in topology.node_templates.items():
                nodes[name] = {
                    "type": node.type if hasattr(node, "type") else None,
                    "properties": node.entity_tpl.get("properties", {}),
                    "requirements": node.entity_tpl.get("requirements", []),
                    "capabilities": list(node.entity_tpl.get("capabilities", {}).keys()),
                }

        if topology.policies:
            for policy_list in topology.policies:
                for policy_name, policy in policy_list.items():
                    policies.append({
                        "name": policy_name,
                        "type": policy.type if hasattr(policy, "type") else None,
                        "targets": policy.targets if hasattr(policy, "targets") else [],
                        "properties": policy.entity_tpl.get("properties", {}),
                    })

        metadata = tosca.metadata or {}

        return {
            "metadata": metadata,
            "nodes": nodes,
            "policies": policies,
            "inputs": list(topology.inputs.keys()) if topology.inputs else [],
            "substitution_mappings": topology.substitution_mappings,
        }


tosca_parser = ToscaParser()
