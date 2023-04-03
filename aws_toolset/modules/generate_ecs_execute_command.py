import boto3, inquirer, sys, json, argparse, os
from .utils import *

def subparser_args_definitions(subparser):
    sub_subparser = subparser.add_parser('generate_ecs_execute_command', help='generate aws ecs execute-command for you')
    #required
    args_definitions(sub_subparser)

def args_definitions(parser):
    #required
    # parser.add_argument("--ta","--targetaddress",dest="TargetAddress",help="REQUIRED: The Amazon Resource Name (ARN) of the Chatbot topic or Chatbot client.", required = True)
    #optional
    parser.add_argument("--c','--cluster",default='', dest="Cluster",help="The Amazon Resource Name (ARN) or short name of the cluster the task is running in. If you do not specify a cluster, the default cluster is assumed.")
    parser.add_argument("--t','--taskid",dest="TaskId",help="The Amazon Resource Name (ARN) or ID of the task the container is part of.")
    parser.add_argument("--cn','--container-name",dest="ContainerName",help="The Amazon Resource Name (ARN) or ID of the task the container is part of.")
    parser.add_argument("--i','--interactive",dest="Interactive", action='store_true',help="Use this flag to run your command in interactive mode.")
    parser.add_argument("--ni','--non-interactive",dest="NonInteractive", action='store_true',help="Use this flag to run your command in interactive mode.")
    parser.add_argument("--cmd','--command",dest="Command",help="The command to run on the container.")
    parser.add_argument("--r','--region",dest="Region",help="The Region to use")
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

def run(args):
    if not args.Region:
        print("no region detected, using default profile region")
        args.Region = get_default_profile_region()
        print(args.Region)
    global ecs_client
    ecs_client = boto3.client('ecs', region_name=args.Region)
    if not args.Cluster:
        print("no user resource detected for cluster, helping user generate them")
        clusters = list_clusters()
        # if not args.Cluster:
        #     sys.exit("No Clusters detected")
        cluster_questions = [
            inquirer.List(
                "cluster",
                message="What Cluster would you like to use?",
                choices=clusters,
            ),
        ]

        answers_cluster = inquirer.prompt(cluster_questions)
        args.Cluster =  answers_cluster["cluster"]
        
        print(args.Cluster)
        if not args.Cluster:
            sys.exit("No Cluster detected")
    if not args.TaskId:
        print("no user resource detected for Task ID, helping user generate them")
        tasks = list_tasks(args.Cluster)
        task_choices = [f"{task['task_id']} ({task['container_name']})" for task in list_tasks_with_containers(args.Cluster,tasks).values()]
        # if not args.Cluster:
        #     sys.exit("No Clusters detected")
        task_questions = [
            inquirer.List(
                "task",
                message="What task would you like to use?",
                choices=task_choices,
            ),
        ]

        answers_task = inquirer.prompt(task_questions)
        args.TaskId = str(answers_task['task']).split(" ")[0]

        print(args.TaskId)
        if not args.TaskId:
            sys.exit("No Task ID detected")
    
    if not args.ContainerName:
        print("no user resource detected for Container Name, helping user generate them")
        container_names = describe_task_container_name(args.Cluster,args.TaskId)
        # if not args.Cluster:
        #     sys.exit("No Clusters detected")
        if len(container_names) != 1:
            container_questions = [
                inquirer.List(
                    "container",
                    message="What container would you like to use?",
                    choices=container_names,
                ),
            ]

            answers_container = inquirer.prompt(container_questions)
            args.ContainerName =  answers_container["container"]
        else:
            print(f"Only one Container Detected, Container name used will be {container_names[0]}")
            args.ContainerName = container_names[0]
        
        print(args.ContainerName)
        if not args.ContainerName:
            sys.exit("No container name detected")

    if not args.Command:
        print("no user resource detected for Command, helping user generate them")
        # if not args.Cluster:
        #     sys.exit("No Clusters detected")
        questions = [
            inquirer.Text("Command", message="Please enter your command"),
        ]

        answers = inquirer.prompt(questions)
        args.Command = answers['Command']
        print(args.Command)
        if not args.Command:
            sys.exit("No Command name detected")

    # interactive_command = "--interactive" if args.interactive else "--non-interactive"
    Command = f'aws ecs execute-command --cluster {args.Cluster} --task {args.TaskId} --container {args.ContainerName} --interactive --command {args.Command} --region {args.Region}'
    print(Command)
    # Run the command and open a Bash shell
    os.system(Command)

def main():
    parser = argparse.ArgumentParser()

    args_definitions(parser)

    args = parser.parse_args()

    run(args)

if __name__ == "__main__":
    main()