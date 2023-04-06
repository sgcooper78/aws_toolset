import boto3, inquirer, sys, json, argparse

try:
    from utils import *
except ModuleNotFoundError:
    from .utils import *

def subparser_args_definitions(subparser):
    sub_subparser = subparser.add_parser('get_ec2_ecs_info', help='help for getting EC2 info from ecs')
    #required
    args_definitions(sub_subparser)

def args_definitions(parser):
    #required
    # parser.add_argument("--ta","--targetaddress",dest="TargetAddress",help="REQUIRED: The Amazon Resource Name (ARN) of the Chatbot topic or Chatbot client.", required = True)
    #optional
    parser.add_argument("--c','--cluster",default='', dest="Cluster",help="Cluster to filter by")
    parser.add_argument("--t','--taskname",dest="Task",help="Service Name to use to get EC2 information")
    # parser.add_argument("--c','--cluster",default='FULL', dest="DetailType", choices=['BASIC', 'FULL'],help="The level of detail to include in the notifications for this resource.")

def run(args):
    if not args.Task:
        if not args.Cluster:
            print("no user resource detected for cluster, helping user generate them")
            clusters = get_all_resource_names("ecs","ecs_clusters")
            # if not args.Cluster:
            #     sys.exit("No Clusters detected")
            cluster_questions = [
                inquirer.List(
                    "cluster",
                    message="What Cluster would you like to use to narrow down services?",
                    choices=clusters,
                ),
            ]

            answers_cluster = inquirer.prompt(cluster_questions)
            args.Cluster =  answers_cluster["cluster"]
        
        print(args.Cluster)
        if not args.Cluster:
            sys.exit("No Cluster detected")

        further_filter_question = [
            inquirer.Confirm("filter", message=f"Would you like to filter down Tasks further than all in the cluster?", default=False),
        ]
        further_filter_bool = inquirer.prompt(further_filter_question)

        tasks = []
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
                tasks = get_sort_resources_by_regex("ecs","ecs_tasks",filter_resources["filter_value"],{"cluster" : args.Cluster})
            elif filter_resources["choice"] == "tags":
                tasks = get_sort_resources_by_tag("ecs","ecs_tasks",json.loads(filter_resources["filter_value"]),{"cluster" : args.Cluster})
            else:
                tasks = get_all_resource_names("ecs","ecs_tasks",{"cluster" : args.Cluster})
            print(tasks)
        else:
            tasks = get_all_resource_names("ecs","ecs_tasks",{"cluster" : args.Cluster})

        task_question = [
            inquirer.List(
                "task",
                message="What Task's would you like info about?",
                choices=tasks,
            ),
        ]

        answers_task = inquirer.prompt(task_question)
        args.Task =  answers_task["task"]

    ec2_container_instances_arns = get_all_resource_names("ecs","ecs_container_instances",{"cluster" : args.Cluster})

    ecs_client = boto3.client('ecs')

    ec2_container_instances = ecs_client.describe_container_instances(
        cluster=args.Cluster,
        containerInstances=ec2_container_instances_arns
    )
    tasks = []
    for instance in ec2_container_instances['containerInstances']:
            # Describe tasks

        t_list_response = ecs_client.list_tasks(
            cluster=args.Cluster,
            containerInstance=instance['containerInstanceArn']
        )

        task_descriptions_response = ecs_client.describe_tasks(
            cluster=args.Cluster,
            tasks=t_list_response['taskArns']
        )

        tasks.append(task_descriptions_response)
    print(tasks)

def main():
    parser = argparse.ArgumentParser()

    args_definitions(parser)

    args = parser.parse_args()

    run(args)

if __name__ == "__main__":
    main()