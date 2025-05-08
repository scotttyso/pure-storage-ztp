#!/usr/bin/env python3
"""Pure Zero Touch Provisioning - 
Use This Module for Pure Storage Zero Touch Provisioning.
It uses argparse to take in the following CLI arguments:
    -dl  or --debug-level:           The Debug Level to Run for Script Output
                                       1. Shows the api request response status code
                                       5. Shows URL String + Lower Options
                                       6. Adds Results + Lower Options
                                       7. Adds json payload + Lower Options
                                     Note: payload shows as pretty and straight to check for stray object types like Dotmap and numpy
    -i  or --ignore-tls:             Ignore TLS server-side certificate verification.  Default is False.
    -y  or --yaml-file:              IMM Transition JSON export to convert to HCL.
"""
#=============================================================================
# Source Modules
#=============================================================================
def prRed(skk): print("\033[91m {}\033[00m" .format(skk))
import os, sys
script_path = os.path.dirname(os.path.realpath(sys.argv[0]))
sys.path.insert(0, f'{script_path}{os.sep}classes')
try:
    #from classes import build, ezfunctions, isight, pcolor, questions, tf, terraform, transition, validating
    from copy import deepcopy
    from dotmap import DotMap
    from json_ref_dict import RefDict, materialize
    from pathlib import Path
    import argparse, json, os, logging, platform, re, requests, urllib3, yaml
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except ImportError as e:
    prRed(f'!!! ERROR !!!\n{e.__class__.__name__}')
    prRed(f" Module {e.name} is required to run this script")
    prRed(f" Install the module using the following: `pip install {e.name}`")
    sys.exit(1)
#=============================================================================
# Log levels 0 = None, 1 = Class only, 2 = Line
#=============================================================================
log_level = 2
#=============================================================================
# Exception Classes and YAML dumper
#=============================================================================
class insufficient_args(Exception): pass

class yaml_dumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(yaml_dumper, self).increase_indent(flow, False)

#=============================================================================
# Function - Basic Setup for the Majority of the modules
#=============================================================================
def base_script_settings(kwargs):
    #=========================================================================
    # Configure logger and Build kwargs
    #=========================================================================
    script_name = (sys.argv[0].split(os.sep)[-1]).split('.')[0]
    dest_dir    = f'{Path.home()}{os.sep}Logs'
    dest_file   = script_name + '.log'
    if not os.path.exists(dest_dir): os.mkdir(dest_dir)
    if not os.path.exists(os.path.join(dest_dir, dest_file)): 
        create_file = f'type nul >> {os.path.join(dest_dir, dest_file)}'; os.system(create_file)
    FORMAT = '%(asctime)-15s [%(levelname)s] [%(filename)s:%(lineno)s] %(message)s'
    logging.basicConfig(filename=f'{dest_dir}{os.sep}{script_name}.log', filemode='a', format=FORMAT, level=logging.DEBUG )
    logger = logging.getLogger('openapi')
    #=========================================================================
    # Determine the Script Path
    #=========================================================================
    args_dict = vars(kwargs.args)
    for k,v in args_dict.items():
        if type(v) == str and v != None: os.environ[k] = v
    kwargs.script_name = (sys.argv[0].split(os.sep)[-1]).split('.')[0]
    kwargs.script_path = os.path.dirname(os.path.realpath(sys.argv[0]))
    kwargs.home        = Path.home()
    kwargs.logger      = logger
    kwargs.op_system   = platform.system()
    kwargs.type_dotmap = type(DotMap())
    kwargs.type_none   = type(None)
    #=========================================================================
    # Import Stored Parameters and Add to kwargs
    #=========================================================================
    ezdata = json.load(open(os.path.join(kwargs.script_path, 'variables', 'schema.json')))
    ezdata.pop('$ref')
    with open(os.path.join(kwargs.script_path, 'variables', 'temp.json'), 'w') as f:
        json.dump(ezdata, f, indent=4)
    ezdata        = materialize(RefDict(os.path.join(kwargs.script_path, 'variables', 'temp.json'), 'r', encoding='utf8'))
    kwargs.ezdata = DotMap(ezdata['components']['schemas'])
    if os.path.exists(os.path.join(kwargs.script_path, 'variables', 'temp.json')):
        os.remove(os.path.join(kwargs.script_path, 'variables', 'temp.json'))
    print(json.dumps(ezdata, indent=4))
    return kwargs
#=============================================================================
# Function: Parse Arguments
#=============================================================================
def cli_arguments():
    parser = argparse.ArgumentParser(description ='Intersight Easy IMM Deployment Module')
    parser.add_argument(
        '-dl', '--debug-level', default = 0,
        help ='Used for troubleshooting.  The Amount of Debug output to Show: '\
            '1. Shows the api request response status code '\
            '5. Show URL String + Lower Options '\
            '6. Adds Results + Lower Options '\
            '7. Adds json payload + Lower Options '\
            'Note: payload shows as pretty and straight to check for stray object types like Dotmap and numpy')
    parser.add_argument(
        '-i', '--ignore-tls', action = 'store_false',
        help   = 'Ignore TLS server-side certificate verification.  Default is False.')
    parser.add_argument('-y', '--yaml-file', default = None,  help = 'The input YAML File.')
    return DotMap(args = parser.parse_args())
#=============================================================================
# Function: Parse YAML File and Build JSON
#=============================================================================
def parse_yaml_file(kwargs):
    parser = argparse.ArgumentParser(description ='Intersight Easy IMM Deployment Module')
    parser.add_argument(
        '-dl', '--debug-level', default = 0,
        help ='Used for troubleshooting.  The Amount of Debug output to Show: '\
            '1. Shows the api request response status code '\
            '5. Show URL String + Lower Options '\
            '6. Adds Results + Lower Options '\
            '7. Adds json payload + Lower Options '\
            'Note: payload shows as pretty and straight to check for stray object types like Dotmap and numpy')
    parser.add_argument(
        '-i', '--ignore-tls', action = 'store_false',
        help   = 'Ignore TLS server-side certificate verification.  Default is False.')
    parser.add_argument('-y', '--yaml-file', default = None,  help = 'The input YAML File.')
    return DotMap(args = parser.parse_args())


#=============================================================================
# Function: Main Script
#=============================================================================
def main():
    #=========================================================================
    # Configure Base Module Setup
    #=========================================================================
    kwargs = cli_arguments()
    kwargs = base_script_settings(kwargs)
    kwargs = parse_yaml_file(kwargs)

if __name__ == '__main__':
    main()