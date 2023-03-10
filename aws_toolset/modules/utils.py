import boto3, re

def get_account_id():
    sts_client = boto3.client("sts")
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sts/client/get_caller_identity.html
    return sts_client.get_caller_identity().get('Account')
    
def get_all_resource_names(resource_type):
    # Create a client for the appropriate resource type
    client = boto3.client(resource_type)

    if resource_type == 'codecommit':
        resource_list = 'repositories'
        resource_key = 'repositoryName'
        paginator = client.get_paginator('list_repositories')
    elif resource_type == 'codebuild':
        resource_list = 'projects'
        resource_key = 'projects'
        paginator = client.get_paginator('list_projects')
    elif resource_type == 'codedeploy':
        resource_list = 'applications'
        resource_key = 'application'
        paginator = client.get_paginator('list_applications')
    elif resource_type == 'codepipeline':
        resource_list = 'pipelines'
        resource_key = 'name'
        paginator = client.get_paginator('list_pipelines')
    else:
        raise ValueError(f"Invalid resource type '{resource_type}'")

    all_resources_names = []

    for page in paginator.paginate():
        if not resource_type == 'codebuild' and not resource_type == 'codedeploy':
                all_resources_names.extend([resource[resource_key] for resource in page[resource_list]])
        else:
            all_resources_names.extend(page[resource_list])

    return all_resources_names

def get_sort_resources_by_regex(service_name, regex_pattern):
    resource_names = get_all_resource_names(service_name)
    
    # Filter the resource names based on the regex pattern
    matching_resources = [name for name in resource_names if re.search(regex_pattern, name)]
    
    # Return the sorted resource names
    return matching_resources

def get_sort_resources_by_tag(service_name, tags_dict):
    """
    Checks if resources in a given service have all specified tags.
    
    :param service_name: The name of the service to check.
    :type service_name: str
    :param tags_dict: A dictionary of tags (keys and values) to check.
    :type tags_dict: dict
    :return: A list of resource names with all the specified tags.
    :rtype: list
    """
    resources_with_tags = []
    
    if service_name == 'codecommit':
        client = boto3.client('codecommit')
        response = client.list_repositories()
        for repository in response['repositories']:
            repository_metadata = client.get_repository(repositoryName=repository['repositoryName'])
            repository_arn = repository_metadata['repositoryMetadata']['Arn']
            tags_response = client.list_tags_for_resource(resourceArn=repository_arn)
            resource_tags = {}
            for tag in tags_response['tags']:
                resource_tags[tag['Key']] = tag['Value']
            if all(tag_key in resource_tags and resource_tags[tag_key] == tag_value for tag_key, tag_value in tags_dict.items()):
                resources_with_tags.append(repository['repositoryName'])
    
    elif service_name == 'codebuild':
        client = boto3.client('codebuild')
        response = client.list_projects()
        for project_name in response['projects']:
            project_metadata = client.batch_get_projects(names=[project_name])['projects'][0]
            project_arn = project_metadata['arn']
            tags_response = client.list_tags_for_resource(resourceArn=project_arn)
            resource_tags = {}
            for tag in tags_response['tags']:
                resource_tags[tag['key']] = tag['value']
            if all(tag_key in resource_tags and resource_tags[tag_key] == tag_value for tag_key, tag_value in tags_dict.items()):
                resources_with_tags.append(project_name)
    
    elif service_name == 'codedeploy':
        client = boto3.client('codedeploy')
        response = client.list_applications()
        for application_name in response['applications']:
            application_metadata = client.get_application(applicationName=application_name)
            application_arn = application_metadata['application']['applicationArn']
            tags_response = client.list_tags_for_resource(ResourceArn=application_arn)
            resource_tags = {}
            for tag in tags_response['tags']:
                resource_tags[tag['Key']] = tag['Value']
            if all(tag_key in resource_tags and resource_tags[tag_key] == tag_value for tag_key, tag_value in tags_dict.items()):
                resources_with_tags.append(application_name)
    
    elif service_name == 'codepipeline':
        client = boto3.client('codepipeline')
        response = client.list_pipelines()
        for pipeline in response['pipelines']:
            pipeline_metadata = client.get_pipeline(name=pipeline['name'])
            pipeline_arn = pipeline_metadata['metadata']['pipelineArn']
            tags_response = client.list_tags_for_resource(resourceArn=pipeline_arn)
            resource_tags = {}
            for tag in tags_response['tags']:
                resource_tags[tag['key']] = tag['value']
            if all(tag_key in resource_tags and resource_tags[tag_key] == tag_value for tag_key, tag_value in tags_dict.items()):
                resources_with_tags.append(pipeline['name'])
    
    return resources_with_tags