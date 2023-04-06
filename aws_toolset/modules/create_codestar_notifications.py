import boto3, inquirer, sys, json, argparse

try:
    from utils import *
except ModuleNotFoundError:
    from .utils import *

def subparser_args_definitions(subparser):
    sub_subparser = subparser.add_parser('create_codestar_notifications', help='help for creating codestar notifications')
    #required
    args_definitions(sub_subparser)

def args_definitions(parser):
    #required
    parser.add_argument("--ta","--targetaddress",dest="TargetAddress",help="REQUIRED: The Amazon Resource Name (ARN) of the Chatbot topic or Chatbot client.", required = True)
    parser.add_argument("--tt','--targettype",dest="TargetType", choices=['SNS', 'AWSChatbotSlack'],help="REQUIRED: The target type. Can be an Chatbot topic or Chatbot client. The options are SNS or AWSChatbotSlack", required = True)
    #optional
    parser.add_argument("--n","--name",dest="Name" ,help="The name for the notification rule. Notification rule names must be unique in your Amazon Web Services account.")
    parser.add_argument("--eti","--eventtypeids", dest="EventTypeIds",help="Should be a list of all accepted notification events. See https://docs.aws.amazon.com/dtconsole/latest/userguide/concepts.html#concepts-api")
    parser.add_argument("--dt','--detailtype",default='FULL', dest="DetailType", choices=['BASIC', 'FULL'],help="The level of detail to include in the notifications for this resource.")
    parser.add_argument("-r", "--resource", dest="Resource", help="either the full arn of the resource. If we are helping you build this list, leave blank")
    parser.add_argument("-t", "--tags" ,default={},help="A list(dict) of tags to apply to this notification rule. Key names cannot start with aws")
    parser.add_argument("-s", "--status", default='ENABLED',choices=['ENABLED', 'DISABLED'],help="The status of the notification rule. The default value is ENABLED . If the status is set to DISABLED , notifications aren't sent for the notification rule.")

#possible resources
# codecommit / codebuild / codedeploy / codepipeline
# https://docs.aws.amazon.com/dtconsole/latest/userguide/concepts.html#concepts-api



def help_user_generate_eventtypeids(resourse):
    print("No eventTypeId's found, helping user generate them")

    EventyTypeChoices = {
        "codecommit" : {
            "codecommit-repository-comments-on-commits","codecommit-repository-comments-on-pull-requests","codecommit-repository-approvals-status-changed","codecommit-repository-approvals-rule-override","codecommit-repository-pull-request-created",
            "codecommit-repository-pull-request-source-updated","codecommit-repository-pull-request-status-changed","codecommit-repository-pull-request-merged","codecommit-repository-branches-and-tags-created",
            "codecommit-repository-branches-and-tags-deleted","codecommit-repository-branches-and-tags-updated"
        }, 
        "codebuild" : { "codebuild-project-build-state-failed", "codebuild-project-build-state-succeeded" , "codebuild-project-build-state-in-progress",
            "codebuild-project-build-state-stopped", "codebuild-project-build-phase-failure", "codebuild-project-build-phase-success"
        }
        , 
        "codedeploy" : {"codedeploy-application-deployment-failed" ,"codedeploy-application-deployment-succeeded", "codedeploy-application-deployment-started" 
        }
        , 
        "codepipeline" : { "codepipeline-pipeline-action-execution-succeeded" , "codepipeline-pipeline-action-execution-failed", "codepipeline-pipeline-action-execution-canceled", "codepipeline-pipeline-action-execution-started",
            "codepipeline-pipeline-stage-execution-started", "codepipeline-pipeline-stage-execution-succeeded", "codepipeline-pipeline-stage-execution-resumed","codepipeline-pipeline-stage-execution-canceled",
            "codepipeline-pipeline-stage-execution-failed","codepipeline-pipeline-pipeline-execution-failed","codepipeline-pipeline-pipeline-execution-canceled" ,"codepipeline-pipeline-pipeline-execution-started","codepipeline-pipeline-pipeline-execution-resumed","codepipeline-pipeline-pipeline-execution-succeeded",
            "codepipeline-pipeline-pipeline-execution-superseded", "codepipeline-pipeline-manual-approval-failed" ,"codepipeline-pipeline-manual-approval-needed" ,"codepipeline-pipeline-manual-approval-succeeded"
        }
    }

    EventTypeIdsQuestion = [
        inquirer.Checkbox(
            "EventTypeIds",
            message="What EventTypeId's do you need?",
            choices=EventyTypeChoices[resourse],
            carousel=False
        ),
    ]

    EventTypeIdsAnswer = inquirer.prompt(EventTypeIdsQuestion)

    return EventTypeIdsAnswer["EventTypeIds"]

def make_codestar_notifications(name: str, event_type_ids: list, resource: str, target_type: str, target_address: str,detail_type: str, status: str, tags: dict = {} ):

    codestar_client = boto3.client('codestar-notifications')

    #https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/codestar-notifications/client/create_notification_rule.html
    if tags:
        response = codestar_client.create_notification_rule(
            Name=name,
            EventTypeIds=event_type_ids,
            Resource=resource,
            Targets=[
                {
                    'TargetType': target_type,
                    'TargetAddress': target_address
                },
            ],
            DetailType=detail_type,
            # ClientRequestToken='string',
            Tags=tags,
            Status=status
        )
    else:
        response = codestar_client.create_notification_rule(
            Name=name,
            EventTypeIds=event_type_ids,
            Resource=resource,
            Targets=[
                {
                    'TargetType': target_type,
                    'TargetAddress': target_address
                },
            ],
            DetailType=detail_type,
            # ClientRequestToken='string',
            # Tags=tags,
            Status=status
        )

    return response['Arn']

def run(args):
    main_resource = ''
    if not args.Resource:
        print("no user resource detected, helping user generate them")
        resources_questions = [
            inquirer.List(
                "resourse",
                message="What Resource would you like to use?",
                choices=["codecommit", "codebuild","codedeploy","codepipeline"],
            ),
        ]

        answers_resources = inquirer.prompt(resources_questions)
        main_resource = answers_resources["resourse"]
        further_filter_question = [
            inquirer.Confirm("filter", message=f"Would you like to filter down further than all?", default=False),
        ]

        further_filter_bool = inquirer.prompt(further_filter_question)

        if further_filter_bool["filter"]:
            further_filter_resources_questions = [
                inquirer.List(
                    "choice",
                    message="What would you like to filter resources down by?",
                    choices=["resource_name","tags"],
                    default=["resource_name"],
                ),
                #{"Environment":"Stage"}
                inquirer.Text("filter_value", message="Enter what you want to filter down by? This is done by regex so doesn't need to be exact, for tags enter the exact tag example tag to enter would be "),
            ]

            filter_resources = inquirer.prompt(further_filter_resources_questions)
            
            if filter_resources["choice"] == "resource_name":
                args.Resource = get_sort_resources_by_regex(answers_resources["resourse"],filter_resources["filter_value"])
            elif filter_resources["choice"] == "tags":
                args.Resource = get_sort_resources_by_tag(answers_resources["resourse"],json.loads(filter_resources["filter_value"]))
        else:
            args.Resource = get_all_resource_names(answers_resources["resourse"])
        print(args.Resource)
    else:
        args.Resource.append(args.Resource)

    if not args.Resource:
        sys.exit("no resources's found, exiting...")

        
    if not args.EventTypeIds:
        args.EventTypeIds = help_user_generate_eventtypeids(answers_resources["resourse"])
        if not args.EventTypeIds:
            sys.exit("no EventTypeId's chosen, exiting...")

    print(args.EventTypeIds)
    
    if not args.Name:
        print("These are your resources")
        print(args.Resource)
        name_question = [
                #{"Environment":"Stage"}
                inquirer.Text("name", message="Since you have multiple resources, the easiest way is to append to each resource name for the notification. Please enter what you would like to be appended to each resource name"),
            ]

        name_answers = inquirer.prompt(name_question)
        args.Name = name_answers['name']
    else:
        args.Name = args.name

    codestar_notifications_arns = []
    for resource in args.Resource:
        resouce_arn = ""
        if main_resource:
            resouce_arn = f"arn:aws:{main_resource}:us-east-1:{get_account_id()}:{resource}"
        else:
            resouce_arn = resource
        codestar_notifications_arns.append(make_codestar_notifications(f"{resource}{args.Name}", args.EventTypeIds, resouce_arn, args.TargetType, args.TargetAddress, args.DetailType, args.status ,args.tags))
    print("here is all the arns of the notifications")
    print(codestar_notifications_arns)

def main():
    parser = argparse.ArgumentParser()

    args_definitions(parser)

    args = parser.parse_args()

    run(args)

if __name__ == "__main__":
    main()