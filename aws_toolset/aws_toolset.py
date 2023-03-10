import argparse, importlib
import importlib.util

#Module Imports 
import modules.create_codestar_notifications as create_codestar_notifications

def create_dict_modules():
    modules = {}
    modules["create_codestar_notifications"] = create_codestar_notifications
    return modules

def parameters_definitions(parser):
    
    modules = create_dict_modules()

    for module in modules:
        try:
            modules[module].args_definitions(parser)
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
        modules[args.Module].main(args)
    except AttributeError:
        print(f"There is no such attribute for {module}")

if __name__ == "__main__":
    main()