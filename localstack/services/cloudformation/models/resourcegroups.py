from localstack.services.cloudformation.deployment_utils import params_list_to_dict
from localstack.services.cloudformation.service_models import GenericBaseModel
from localstack.utils.aws import aws_stack


class ResourceGroupsGroup(GenericBaseModel):
    @staticmethod
    def cloudformation_type():
        return "AWS::ResourceGroups::Group"

    def fetch_state(self, stack_name, resources):
        client = aws_stack.connect_to_service("resource-groups")
        result = client.list_groups().get("Groups", [])
        result = [g for g in result if g["Name"] == self.props["Name"]]
        return (result or [None])[0]

    def get_cfn_attribute(self, attribute_name):
        if attribute_name == "Arn":
            return self.props.get("GroupArn")

    @classmethod
    def get_deploy_templates(cls):
        def _set_physical_resource_id(
            result: dict, resource_id: str, resources: dict, resource_type: str
        ):
            resources[resource_id]["PhysicalResourceId"] = result["Group"]["Name"]

        return {
            "create": {
                "function": "create_group",
                "parameters": {
                    "Name": "Name",
                    "Description": "Description",
                    "ResourceQuery": "ResourceQuery",
                    "Configuration": "Configuration",
                    "Tags": params_list_to_dict("Tags"),
                },
                "result_handler": _set_physical_resource_id,
            },
            "delete": {"function": "delete_group", "parameters": {"Group": "Name"}},
        }
