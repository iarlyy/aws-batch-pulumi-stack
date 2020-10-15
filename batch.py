from pulumi import ComponentResource, ResourceOptions
import pulumi_aws as aws

class ComponentArgs:

  def __init__(
                self,
                name=None,
                vpc_id=None,
                subnets=[],
                instance_types=["c5.large"],
                min_vcpus=1,
                max_vcpus=256,
                sg_id=None,
                key_pair=None
              ):
    self.name = name
    self.vpc_id = vpc_id
    self.subnets = subnets
    self.sg_id = sg_id
    self.instance_types = instance_types
    self.min_vcpus = min_vcpus
    self.max_vcpus = max_vcpus
    self.key_pair = key_pair

class BatchWorkload(ComponentResource):

  def __init__(
                self, 
                name: str,
                args: ComponentArgs,
                opts: ResourceOptions = None
              ):    

      super().__init__("my:modules:BatchWorkload", name, {}, opts)

      task_role = aws.iam.Role("{}-task_role".format(name),
          name="{}-task".format(name),
          assume_role_policy="""{
        "Version": "2012-10-17",
        "Statement": [
          {
            "Action": "sts:AssumeRole",
            "Principal": {
              "Service": "ecs-tasks.amazonaws.com"
            },
            "Effect": "Allow"
          }
        ]
      }
      """,
        tags={}
      )


      compute_role = aws.iam.Role("{}-compute_role".format(name),
          name="{}-compute".format(name),
          assume_role_policy="""{
        "Version": "2012-10-17",
        "Statement": [
          {
            "Action": "sts:AssumeRole",
            "Principal": {
              "Service": "batch.amazonaws.com"
            },
            "Effect": "Allow",
            "Sid": ""
          }
        ]
      }
      """,
        tags={}
      )

      ec2_role = aws.iam.Role("{}-ec2_compute_role".format(name),
          name="{}-ec2".format(name),
          assume_role_policy="""{
        "Version": "2012-10-17",
        "Statement": [
          {
            "Action": "sts:AssumeRole",
            "Principal": {
              "Service": "ec2.amazonaws.com"
            },
            "Effect": "Allow",
            "Sid": ""
          }
        ]
      }
      """,
        tags={}
      )

      task_policy = aws.iam.Policy("{}-task_policy".format(name),
          name="{}-task-policy".format(name),
          policy="""{
        "Version": "2012-10-17",
        "Statement": [
          {
            "Action": [
              "s3:*"
            ],
            "Effect": "Allow",
            "Resource": "*"
          }
        ]
      }
      """
      )

      instance_profile = aws.iam.InstanceProfile("{}-compute_instance_profile".format(name), 
        name="{}-instance-profile".format(name),
        role=ec2_role.name
      )

      attach_bach_task_policy = aws.iam.RolePolicyAttachment("{}-attach_task_policy".format(name),
        policy_arn=task_policy.arn,
        role=task_role.name
      )

      attach_bach_service_policy = aws.iam.RolePolicyAttachment("{}-attach_ec2_role".format(name),
        policy_arn='arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role',
        role=ec2_role.name
      )

      attach_bach_service_role = aws.iam.RolePolicyAttachment("{}-attach_service_role".format(name),
        policy_arn='arn:aws:iam::aws:policy/service-role/AWSBatchServiceRole',
        role=compute_role.name
      )

      compute_env = aws.batch.ComputeEnvironment("{}-compute_env".format(name),
        compute_environment_name="{}".format(name),
        compute_resources=aws.batch.ComputeEnvironmentComputeResourcesArgs(
          instance_role=instance_profile.arn,
          instance_types=args.instance_types,
          min_vcpus = args.min_vcpus,
          max_vcpus = args.max_vcpus, 
          type = 'EC2',
          security_group_ids=args.sg_id,
          subnets=args.subnets,
          ec2_key_pair=args.key_pair
        ),
        service_role=compute_role.arn,
        type='MANAGED',
        opts=ResourceOptions(depends_on=[instance_profile, task_role, compute_role, ec2_role])
      )

      job_queue = aws.batch.JobQueue("{}-queue".format(name),
        name="{}".format(name),
        state="ENABLED",
        priority=1,
        compute_environments=[
          compute_env.arn
        ] 
      )
