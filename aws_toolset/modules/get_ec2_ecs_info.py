import boto3, inquirer, sys, json, argparse
from utils import *

def args_definitions(subparser):
    sub_subparser = subparser.add_parser('get_ec2_ecs_info', help='help for getting EC2 info from ecs')
    #required
    # sub_subparser.add_argument("--ta","--targetaddress",dest="TargetAddress",help="REQUIRED: The Amazon Resource Name (ARN) of the Chatbot topic or Chatbot client.", required = True)
    #optional
    sub_subparser.add_argument("--c','--cluster",default='', dest="Cluster",help="Cluster to filter by")
    sub_subparser.add_argument("--s','--servicename",dest="Service",help="Service Name to use to get EC2 information")
    # sub_subparser.add_argument("--c','--cluster",default='FULL', dest="DetailType", choices=['BASIC', 'FULL'],help="The level of detail to include in the notifications for this resource.")

def run(args):
    if not args.Service:
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
            args.Cluster =  answers_cluster["clusters"]
        
        print(args.Cluster)
        if not args.Cluster:
            sys.exit("No Cluster detected")

        further_filter_question = [
            inquirer.Confirm("filter", message=f"Would you like to filter down Services further than all in the cluster?", default=False),
        ]
        further_filter_bool = inquirer.prompt(further_filter_question)

        services = []
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
                services = get_sort_resources_by_regex("ecs","ecs_services",filter_resources["filter_value"],{"cluster" : args.Cluster})
            elif filter_resources["choice"] == "tags":
                services = get_sort_resources_by_tag("ecs","ecs_services",json.loads(filter_resources["filter_value"]),{"cluster" : args.Cluster})
            else:
                services = get_all_resource_names("ecs","ecs_services",{"cluster" : args.Cluster})
            print(services)
        else:
            services = get_all_resource_names("ecs","ecs_services", args.Cluster)

        service_question = [
            inquirer.List(
                "service",
                message="What Service would you like info about?",
                choices=services,
            ),
        ]

        answers_service = inquirer.prompt(service_question)
        args.Service =  answers_service["clusters"]

    print(args.Service)

    ec2_container_instances_arns = get_all_resource_names("ecs","ecs_container_instances",{"cluster" : args.Cluster})

    ecs_client = boto3.client('ecs')

    ec2_container_instances = ecs_client.describe_container_instances(
        cluster=args.Cluster,
        containerInstances=ec2_container_instances_arns
    )
    tasks = []
    for instance in ec2_container_instances['containerInstances']:
        if instance['ec2InstanceId'] == "EC2":

            # List tasks on this container instance
            task_list_response = ecs_client.list_tasks(
                cluster=args.Cluster,
                containerInstance=instance['containerInstanceArn']
            )

            # Describe tasks
            task_descriptions_response = ecs_client.describe_tasks(
                cluster=args.Cluster,
                tasks=task_list_response['taskArns']
            )

            tasks.append(task_descriptions_response)
    print(tasks)

def main():
    parser = argparse.ArgumentParser()

    subparser = parser.add_subparsers(dest="Module",title='Modules',description='List of Modules',help='List of modules')

    args_definitions(subparser)

    args = parser.parse_args()

    run(args)

if __name__ == "__main__":
    main()