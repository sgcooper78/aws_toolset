# aws_toolset
AWS Toolset
These tools are intended to help AWS developers automate tasks that they frequently perform, making it simpler to manage cloud resources. In the course of working with AWS, you may find yourself performing the same tasks repeatedly, which can be time-consuming and monotonous. This toolset aims to simplify these tasks by providing a variety of scripts that automate tasks such as retrieving EC2 and ECS information, managing S3 buckets, and working with CloudFormation stacks. The scripts can be run as a command-line interface (CLI) or through the Python `-m` interface. Additionally, they can be easily installed with pip to facilitate access.

By using these tools, you can save time and focus on more critical aspects of your work. The aim of this toolset is to streamline your workflow and make your life as an AWS developer more straightforward.

    pip install aws_toolset
    aws_toolset module

or

    python3 aws_toolset module

or

    python3 -m aws_toolset module

## Import

If you need to import then

from aws_toolset import aws_toolset

from aws_toolset.module import create_codestar_notifications

## options

- Module This is the module that it will run, The list of modules can be seen with the -h option

## Modules

### create_codestar_notifications
This module is to help in the creation of codestar notifications

### options
- --ta REQUIRED: The Amazon Resource Name (ARN) of the Chatbot topic or Chatbot client.
- --tt REQUIRED: The target type. Can be an Chatbot topic or Chatbot client. The options are SNS or AWSChatbotSlack"
- --n The name for the notification rule. Notification rule names must be unique in your Amazon Web Services account.
- --eti Should be a list of all accepted notification events. See https://docs.aws.amazon.com/dtconsole/latest/userguide/concepts.html#concepts-api
- --dt The level of detail to include in the notifications for this resource.
- --r either the full arn of the resource. If we are helping you build this list, leave blank
- -t A list(dict) of tags to apply to this notification rule. Key names cannot start with aws
- -s The status of the notification rule. The default value is ENABLED . If the status is set to DISABLED , notifications aren't sent for the notification rule.

### generate_ecs_execute_command
This module is to help create the ecs exec command from your cli. It can also run it. Must have AWS CLI and AWS Session Manager Plugin installed.

### options
- --c or --cluster  The Amazon Resource Name (ARN) or short name of the cluster the task is running in. If you do not specify a cluster, the default cluster is assumed.
- --t or --taskid The Amazon Resource Name (ARN) or ID of the task the container is part of.
- --cn or --container-name The name of the container to execute the command on.
- --i or --interactive Use this flag to run your command in interactive mode.
- --cmd or --commandThe command to run on the container.
- --r or --region The Region to use
- 
### get_ec2_ecs_info
This module is to get info about ecs. Specifically to get from a container and tell what ec2 instances it's running on.

### options
- --c or --cluster  The Amazon Resource Name (ARN) or short name of the cluster the task is running in. If you do not specify a cluster, the default cluster is assumed.
- --cn or --container-name Container name to give to filter by
- --r or --region The Region to use
- --f or --full-output Option to give all details or not
