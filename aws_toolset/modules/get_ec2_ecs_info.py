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
    parser.add_argument("--cn','--containername",dest="ContainerName",help="Service Name to use to get EC2 information")
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

def question_single_list(list,type):
    cluster_questions = [
        inquirer.List(
            "answer",
            message=f"What {type} would you like to use?",
            choices=list,
        ),
    ]

    answers_cluster = inquirer.prompt(cluster_questions)
    return answers_cluster["answer"]

def question_single_confirm(Text,default):
    questions = [
        inquirer.Confirm("Confirm", message=Text,default=default),
    ]
    answers = inquirer.prompt(questions)
    return answers["Confirm"]

def question_single_text(Text):
    questions = [
        inquirer.Text("Text", message=Text),
    ]

    answers = inquirer.prompt(questions)
    return answers['Text']

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

    ec2_container_instances_arns = get_all_resource_names("ecs","ecs_container_instances",{"cluster" : args.Cluster})

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


    print(tasks)

def main():
    parser = argparse.ArgumentParser()

    args_definitions(parser)

    args = parser.parse_args()

    run(args)

if __name__ == "__main__":
    main()