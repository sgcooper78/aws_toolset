import boto3, inquirer, sys, json
from .utils import *

def args_definitions(subparser):
    sub_subparser = subparser.add_parser('get_ec2_ecs_info', help='help for getting EC2 info from ecs')
    #required
    # sub_subparser.add_argument("--ta","--targetaddress",dest="TargetAddress",help="REQUIRED: The Amazon Resource Name (ARN) of the Chatbot topic or Chatbot client.", required = True)
    #optional
    sub_subparser.add_argument("--c','--cluster", dest="Cluster",help="Cluster to filter by")
    sub_subparser.add_argument("--s','--servicename",dest="ServiceName",help="Service Name to use to get EC2 information")
    # sub_subparser.add_argument("--c','--cluster",default='FULL', dest="DetailType", choices=['BASIC', 'FULL'],help="The level of detail to include in the notifications for this resource.")

def main(args):
    main_resource = ''
    if not args.Cluster:
        print("no user resource detected, helping user generate them")
        resources_questions = [
            inquirer.List(
                "resourse",
                message="What Cluster would you like to use to narrow down services?",
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

    


if __name__ == "__main__":
    main(args)