import os

import pytest

from localstack.utils.common import short_uid


def test_bucketpolicy(
    cfn_client,
    s3_client,
    deploy_cfn_template,
):
    bucket_name = f"ls-bucket-{short_uid()}"
    deploy_result = deploy_cfn_template(
        template_path=os.path.join(
            os.path.dirname(__file__), "../../templates/s3_bucketpolicy.yaml"
        ),
        parameters={"BucketName": bucket_name},
        template_mapping={"include_policy": True},
    )
    bucket_policy = s3_client.get_bucket_policy(Bucket=bucket_name)["Policy"]
    assert bucket_policy

    deploy_cfn_template(
        is_update=True,
        stack_name=deploy_result.stack_id,
        parameters={"BucketName": bucket_name},
        template_path=os.path.join(
            os.path.dirname(__file__), "../../templates/s3_bucketpolicy.yaml"
        ),
        template_mapping={"include_policy": False},
    )
    with pytest.raises(Exception) as err:
        s3_client.get_bucket_policy(Bucket=bucket_name).get("Policy")

    assert err.value.response["Error"]["Code"] == "NoSuchBucketPolicy"


def test_bucket_autoname(cfn_client, deploy_cfn_template):
    result = deploy_cfn_template(
        template_path=os.path.join(
            os.path.dirname(__file__), "../../templates/s3_bucket_autoname.yaml"
        )
    )
    descr_response = cfn_client.describe_stacks(StackName=result.stack_id)
    output = descr_response["Stacks"][0]["Outputs"][0]
    assert output["OutputKey"] == "BucketNameOutput"
    assert result.stack_name.lower() in output["OutputValue"]


def test_bucket_versioning(cfn_client, deploy_cfn_template, s3_client):
    result = deploy_cfn_template(
        template_path=os.path.join(
            os.path.dirname(__file__), "../../templates/s3_versioned_bucket.yaml"
        )
    )
    assert "BucketName" in result.outputs
    bucket_name = result.outputs["BucketName"]
    bucket_version = s3_client.get_bucket_versioning(Bucket=bucket_name)
    assert bucket_version["Status"] == "Enabled"


def test_cors_configuration(cfn_client, deploy_cfn_template, s3_client, snapshot):
    snapshot.add_transformer(snapshot.transform.cloudformation_api())
    snapshot.add_transformer(snapshot.transform.s3_api())

    bucket_name = f"ls-bucket-{short_uid()}"
    result = deploy_cfn_template(
        template_path=os.path.join(
            os.path.dirname(__file__), "../../templates/s3_cors_bucket.yaml"
        ),
        parameters={"BucketName": bucket_name},
        max_wait=300,
    )
    assert "BucketName" in result.outputs
    bucket_name = result.outputs["BucketName"]
    cors_info = s3_client.get_bucket_cors(Bucket=bucket_name)

    snapshot.match("cors_info", cors_info)
