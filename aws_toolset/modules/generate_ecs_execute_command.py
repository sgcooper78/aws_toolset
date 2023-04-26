import boto3, sys, argparse, os

try:
    from utils import *
except ModuleNotFoundError:
    from .utils import *

def subparser_args_definitions(subparser):
    sub_subparser = subparser.add_parser('generate_ecs_execute_command', help='generate aws ecs execute-command for you')
    #required
    args_definitions(sub_subparser)

def args_definitions(parser):
    #required
    # parser.add_argument("--ta","--targetaddress",dest="TargetAddress",help="REQUIRED: The Amazon Resource Name (ARN) of the Chatbot topic or Chatbot client.", required = True)
    #optional
    parser.add_argument("--c","--cluster",default='', dest="Cluster",help="The Amazon Resource Name (ARN) or short name of the cluster the task is running in. If you do not specify a cluster, the default cluster is assumed.")
    parser.add_argument("--t","--taskid",dest="TaskId",help="The Amazon Resource Name (ARN) or ID of the task the container is part of.")
    parser.add_argument("--cn","--container-name",dest="ContainerName",help="The name of the container to execute the command on.")
    parser.add_argument("--i","--interactive",dest="Interactive", action='store_true',help="Use this flag to run your command in interactive mode.")
    parser.add_argument("--cmd","--command",dest="Command",help="The command to run on the container.")
    parser.add_argument("--r","--region",dest="Region",help="The Region to use")
    # parser.add_argument("--c','--cluster",default='FULL', dest="DetailType", choices=['BASIC', 'FULL'],help="The level of detail to include in the notifications for this resource.")

def list_clusters():
    paginator = ecs_client.get_paginator('list_clusters')

    all_resources_names = []
    for page in paginator.paginate():
        all_resources_names.extend(page["clusterArns"])

    return all_resources_names

def list_tasks(cluster):
    paginator = ecs_client.get_paginator('list_tasks')

    all_resources_names = []
    for page in paginator.paginate(cluster=cluster):
        all_resources_names.extend(page["taskArns"])

    return all_resources_names

def list_services(cluster):
    paginator = ecs_client.get_paginator('list_services')

    all_resources_names = []
    for page in paginator.paginate(cluster=cluster):
        all_resources_names.extend(page["serviceArns"])

    return all_resources_names

def list_tasks_with_containers(cluster,taskids):
    
    response = ecs_client.describe_tasks(
        cluster=cluster,
        tasks=taskids
    )
    container_names = {}
    for task in response['tasks']:
        task_id = task['taskArn']
        container_name = next(iter(task['containers']))['name']
        container_names[task_id] = {
            'task_id': task_id,
            'container_name': container_name
        }
    return container_names

def describe_services(cluster,services):
    
    response = ecs_client.describe_services(
        cluster=cluster,
        services=services
    )
    return response

def describe_task_container_name(cluster,taskid):
    
    response = ecs_client.describe_tasks(
        cluster=cluster,
        tasks=[
            taskid,
        ]
    )

    container_names = []
    for container in response['tasks'][0]['containers']:
        container_names.append(container['name'])
    return container_names

def get_tasks(cluster,service_name):
    response = ecs_client.list_tasks(cluster=cluster, serviceName=service_name)
    tasks = response['taskArns']

    task_ids = []
    for task_arn in tasks:
        task_ids.append(task_arn.split("/")[-1])
    return task_ids

def run(args):
    if not args.Region:
        print("no region detected, using default profile region")
        args.Region = get_default_profile_region()
        print(args.Region)
    global ecs_client
    ecs_client = boto3.client('ecs', region_name=args.Region)
    if not args.Cluster:
        print("no user resource detected for cluster, helping user generate them")

        args.Cluster =  question_single_list(list_clusters(),"Cluster")
        
        print(f"{args.Cluster} has been chosen")
        if not args.Cluster:
            sys.exit("No Cluster detected")
    if not args.TaskId:
        print("no user resource detected for Task ID, helping user generate them")

        args.Service = question_single_list(list_services(args.Cluster),"Service")

        task_ids = get_tasks(args.Cluster,args.Service)

        # print(task_ids)
        if len(task_ids) > 1:
            args.TaskId =  question_single_list(task_ids,"Task")
        elif len(task_ids) == 1:
            print(f"Only one task detected, you will be using {task_ids[0]}")
            args.TaskId = task_ids[0]
        else:
            sys.exit("No Tasks detected, exiting...")

        if not args.TaskId:
            sys.exit("No Task ID detected")
    
    if not args.ContainerName:
        print("no user resource detected for Container Name, helping user generate them")
        container_names = describe_task_container_name(args.Cluster,args.TaskId)
        # if not args.Cluster:
        #     sys.exit("No Clusters detected")
        if len(container_names) != 1:
            args.ContainerName =  question_single_list(describe_task_container_name(args.Cluster,args.TaskId),"Container")
        else:
            print(f"Only one Container Detected, Container name {container_names[0]} will be used")
            args.ContainerName = container_names[0]
        
        print(args.ContainerName)
        if not args.ContainerName:
            sys.exit("No container name detected")

    if not args.Command:
        print("no user resource detected for Command, helping user generate them")
        args.Command = question_single_text("Please enter your command")
        
        if not args.Command:
            sys.exit("No Command name detected")
        else:
            print(f"{args.Command} has been chosen as the command")

    interactive_command = "--interactive" if args.Interactive else "--non-interactive"
    command_to_run = f'aws ecs execute-command --cluster {args.Cluster} --task {args.TaskId} --container {args.ContainerName} {interactive_command} --command {args.Command} --region {args.Region}'
    print(command_to_run)

    if question_single_confirm(f"Do you want to run the command {command_to_run}?",True):
        # Run the command and open a Bash shell
        os.system(command_to_run)

def main():
    parser = argparse.ArgumentParser()

    args_definitions(parser)

    args = parser.parse_args()

    run(args)

if __name__ == "__main__":
    main()