
  

# aws_toolset

  

AWS Toolset

  

is a set of tools that I created for the every lazy AWS Developer. Why? When your in AWS you

will find that there is a subset of tasks. You then will abstract them into a script.

As I find these I am putting these here for the other developers to use so they can use them.

  
  
  

The tool can be ran directory as a CLI or with the python -m interface or installed with pip.

    pip install aws_toolset

or

    aws_toolset module

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

## options

  

- --ta REQUIRED: The Amazon Resource Name (ARN) of the Chatbot topic or Chatbot client.

- --tt REQUIRED: The target type. Can be an Chatbot topic or Chatbot client. The options are SNS or AWSChatbotSlack"

- --n The name for the notification rule. Notification rule names must be unique in your Amazon Web Services account.

- --eti Should be a list of all accepted notification events. See https://docs.aws.amazon.com/dtconsole/latest/userguide/concepts.html#concepts-api

- --dt The level of detail to include in the notifications for this resource.

- --r either the full arn of the resource. If we are helping you build this list, leave blank

- -t A list(dict) of tags to apply to this notification rule. Key names cannot start with aws

- -s The status of the notification rule. The default value is ENABLED . If the status is set to DISABLED , notifications aren't sent for the notification rule.


