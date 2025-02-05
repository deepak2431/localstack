from localstack.services.cloudformation.deployment_utils import generate_default_name
from localstack.services.cloudformation.service_models import GenericBaseModel
from localstack.utils.aws import aws_stack


class LogsLogGroup(GenericBaseModel):
    @staticmethod
    def cloudformation_type():
        return "AWS::Logs::LogGroup"

    def get_cfn_attribute(self, attribute_name):
        props = self.props
        if attribute_name == "Arn":
            return props.get("arn")
        return super(LogsLogGroup, self).get_cfn_attribute(attribute_name)

    def fetch_state(self, stack_name, resources):
        group_name = self.props.get("LogGroupName")
        logs = aws_stack.connect_to_service("logs")
        groups = logs.describe_log_groups(logGroupNamePrefix=group_name)["logGroups"]
        return ([g for g in groups if g["logGroupName"] == group_name] or [None])[0]

    @staticmethod
    def add_defaults(resource, stack_name: str):
        name = resource.get("Properties", {}).get("LogGroupName")
        if not name:
            resource["Properties"]["LogGroupName"] = generate_default_name(
                stack_name, resource["LogicalResourceId"]
            )

    @staticmethod
    def get_deploy_templates():
        def _set_physical_resource_id(
            result: dict, resource_id: str, resources: dict, resource_type: str
        ):
            resource = resources[resource_id]
            resource["PhysicalResourceId"] = resource["Properties"]["LogGroupName"]

        return {
            "create": {
                "function": "create_log_group",
                "parameters": {"logGroupName": "LogGroupName"},
                "result_handler": _set_physical_resource_id,
            },
            "delete": {
                "function": "delete_log_group",
                "parameters": {"logGroupName": "LogGroupName"},
            },
        }


class LogsLogStream(GenericBaseModel):
    @staticmethod
    def cloudformation_type():
        return "AWS::Logs::LogStream"

    def get_cfn_attribute(self, attribute_name):
        return super(LogsLogStream, self).get_cfn_attribute(attribute_name)

    def fetch_state(self, stack_name, resources):
        group_name = self.props.get("LogGroupName")
        stream_name = self.props.get("LogStreamName")
        logs = aws_stack.connect_to_service("logs")
        streams = logs.describe_log_streams(
            logGroupName=group_name, logStreamNamePrefix=stream_name
        )["logStreams"]
        return ([s for s in streams if s["logStreamName"] == stream_name] or [None])[0]

    @staticmethod
    def add_defaults(resource, stack_name: str):
        name = resource.get("Properties", {}).get("LogStreamName")
        if not name:
            resource["Properties"]["LogStreamName"] = generate_default_name(
                stack_name, resource["LogicalResourceId"]
            )

    @staticmethod
    def get_deploy_templates():
        def _set_physical_resource_id(
            result: dict, resource_id: str, resources: dict, resource_type: str
        ):
            resource = resources[resource_id]
            resource["PhysicalResourceId"] = resource["Properties"]["LogStreamName"]

        return {
            "create": {
                "function": "create_log_stream",
                "parameters": {"logGroupName": "LogGroupName", "logStreamName": "LogStreamName"},
                "result_handler": _set_physical_resource_id,
            },
            "delete": {
                "function": "delete_log_stream",
                "parameters": {"logGroupName": "LogGroupName", "logStreamName": "LogStreamName"},
            },
        }


class LogsSubscriptionFilter(GenericBaseModel):
    @staticmethod
    def cloudformation_type():
        return "AWS::Logs::SubscriptionFilter"

    def fetch_state(self, stack_name, resources):
        props = self.props
        group_name = props.get("LogGroupName")
        filter_pattern = props.get("FilterPattern")
        logs = aws_stack.connect_to_service("logs")
        groups = logs.describe_subscription_filters(logGroupName=group_name)["subscriptionFilters"]
        groups = [g for g in groups if g.get("filterPattern") == filter_pattern]
        return (groups or [None])[0]

    @staticmethod
    def get_deploy_templates():
        def _set_physical_resource_id(
            result: dict, resource_id: str, resources: dict, resource_type: str
        ):
            resource = resources[resource_id]
            resource["PhysicalResourceId"] = resource["Properties"]["LogGroupName"]

        return {
            "create": {
                "function": "put_subscription_filter",
                "parameters": {
                    "logGroupName": "LogGroupName",
                    "filterName": "LogGroupName",  # there can only be one filter associated with a log group
                    "filterPattern": "FilterPattern",
                    "destinationArn": "DestinationArn",
                },
                "result_handler": _set_physical_resource_id,
            },
            "delete": {
                "function": "delete_subscription_filter",
                "parameters": {
                    "logGroupName": "LogGroupName",
                    "filterName": "LogGroupName",
                },
            },
        }
