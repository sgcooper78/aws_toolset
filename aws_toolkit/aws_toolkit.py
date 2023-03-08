import argparse, importlib
from pathlib import Path

def create_dict_modules():
    modules = {}
    p = Path(r'./modules').glob('**/*.py')
    files = [x for x in p if x.is_file()]
    # print(files)
    for file in files:
        fileString = str(file)
        if not "__init__" in fileString:
            module_path = fileString.replace("/",".")[:-3]
            module_name = module_path.split('.')[-1]
            modules[module_name] = module_path
    return modules

def parameters_definitions(parser):
    
    modules = create_dict_modules()
    # print(modules)
    for module in modules.values():
        if not "__init__" in module:
            try:
                module = importlib.import_module(f"{module}")
            except ImportError:
                # print(f"Could not import {module}")
                pass
                
            try:
                module.args_definitions(parser)
            except AttributeError:
                # print(f"There is no such attribute for {module}")
                pass

def main():
    parser = argparse.ArgumentParser()

    subparser = parser.add_subparsers(dest="Module",title='Modules',description='List of Modules',help='List of modules', required = True)
    # parser.add_argument("-v", "--verbose", default=False, action="store_true" ,help="Increase verbosity of program" )

    parameters_definitions(subparser)

    args = parser.parse_args()

    modules = create_dict_modules()

    module = importlib.import_module(f'{modules[args.Module]}')

    module.main(args)

if __name__ == "__main__":
    main()