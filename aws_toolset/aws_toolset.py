import argparse

#Module Imports 
try:
    from modules import create_codestar_notifications
    from modules import get_ec2_ecs_info
    from modules import generate_ecs_execute_command
except ModuleNotFoundError:
    from .modules import create_codestar_notifications
    from .modules import get_ec2_ecs_info
    from .modules import generate_ecs_execute_command


def create_dict_modules():
    modules = {}
    modules["create_codestar_notifications"] = create_codestar_notifications
    modules["get_ec2_ecs_info"] = get_ec2_ecs_info
    modules["generate_ecs_execute_command"] = generate_ecs_execute_command

    return modules

def parameters_definitions(parser):
    
    modules = create_dict_modules()

    for module in modules:
        try:
            modules[module].subparser_args_definitions(parser)
        except AttributeError:
            # print(f"There is no such attribute for {mod}")
            pass
        

def main():
    parser = argparse.ArgumentParser()

    subparser = parser.add_subparsers(dest="Module",title='Modules',description='List of Modules',help='List of modules', required = True)
    # parser.add_argument("-v", "--verbose", default=False, action="store_true" ,help="Increase verbosity of program" )

    parameters_definitions(subparser)

    args = parser.parse_args()

    modules = create_dict_modules()

    try:
        modules[args.Module].run(args)
    except AttributeError:
        print(f"There is no such attribute for {modules[args.Module]}")

if __name__ == "__main__":
    main()