from env_values import development
import batch

batch_workload = batch.BatchWorkload(
    'aws-batch-pulumi-stack-test',
    batch.ComponentArgs(
        name='aws-batch-pulumi-stack-test',
        subnets=private_subnet_ids,
        sg_id=sg_id,
        min_vcpus=2,
        key_pair='development'
    )
)
