import argparse, importlib
import importlib.util
from pathlib import Path

class ModuleInfo:
    def __init__(self, module_path, module_file_path):
        self.module_path = module_path
        self.module_file_path = module_file_path

def create_dict_modules():
    modules = {}
    actual_path = Path(__file__).parent.resolve()
    # print(actual_path)
    path_to_modules = str(actual_path) + '/modules'
    p = Path(path_to_modules).glob('**/*.py')
    files = [x for x in p if x.is_file()]
    # print(files)
    for file in files:
        fileString = str(file)
        if not "__init__" in fileString:
            module_file_path = fileString
            module_path = fileString.replace("/",".")[:-3]
            module_name = module_path.split('.')[-1]
            module_sub_name = module_path.split('.')[-2]
            modules[module_name] = ModuleInfo(f"{module_sub_name}.{module_name}" , module_file_path)
    return modules

def parameters_definitions(parser):
    
    modules = create_dict_modules()

    for module in modules.values():
        try:
            spec = importlib.util.spec_from_file_location(module.module_path, module.module_file_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
        except ImportError:
            print(f"Could not import {mod}")
            pass
                
        try:
            mod.args_definitions(parser)
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

    module = ''
    try:
        spec = importlib.util.spec_from_file_location(modules[args.Module].module_path, modules[args.Module].module_file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except ImportError:
        print(f"Could not import {module}")

    try:
        module.main(args)
    except AttributeError:
        print(f"There is no such attribute for {module}")

if __name__ == "__main__":
    main()