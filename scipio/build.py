"""Build xcode projects and workspaces using xcodebuild"""

from glob import glob
from re import search, UNICODE
import subprocess
from os import chdir, path
from shutil import move

def parse_xcodebuild_list(output_string):
    """Decompose xcode -list output to lists"""
    lines = output_string.splitlines()
    gathering = ''
    target_list = []
    configurations_list = []
    schemes_list = []
    for line in lines:
        if line == '    Targets:':
            gathering = 'targets'
        elif line == '    Build Configurations:':
            gathering = 'configurations'
        elif line == '    Schemes:':
            gathering = 'schemes'
        elif not line:
            gathering = ''
        elif gathering:
            if gathering == 'targets':
                target_list.append(line.strip())
            elif gathering == 'configurations':
                configurations_list.append(line.strip())
            elif gathering == 'schemes':
                schemes_list.append(line.strip())
    return target_list, configurations_list, schemes_list


def run_build(command, verbose, project):
    """Run the build command through xcodebuild"""
    try:
        if verbose:
            output = subprocess.check_output(command)
            print(output.decode('utf-8', 'replace'))
        else:
            subproc = subprocess.Popen(command, stdout=subprocess.PIPE)
            grep = subprocess.Popen(['grep', '-A', '5', '-E', r'(error|warning):'],
                                    stdin=subproc.stdout, stdout=subprocess.PIPE)
            subproc.stdout.close()
            output = grep.communicate()[0]
            subproc.wait()

            #move built framework files to the calling folder (including to the original/top level)
            frameworks = glob('./build/*/*.framework')
            if frameworks:
                for outfile in frameworks:
                    move(outfile, '../../' + path.basename(outfile))
            # tell em you're done
            manual = ''
            for elem in command:
                if ' ' in elem:
                    manual += "'" + elem + "' "
                else:
                    manual += elem + ' '
            print('Built: ' + project + ' ' + manual)
    except subprocess.CalledProcessError as err:
        print(err.output.decode('utf-8', 'replace'))


def setup_build(project, possible_args, workspace=False):
    """Go to the folder/project or folder/workspace and check if any of the configuration, sdk,
    scheme, or target args supplied exist in it, set up the build with as many of them as do"""
    proj_info = project.split('/') # folder/project
    chdir('./' + proj_info[0]) # all of the project files are in here

    if workspace:
        w_or_p_flag = '-workspace'
    else:
        w_or_p_flag = '-project'

    output = subprocess.check_output(['xcodebuild',
                                      '-list',
                                      w_or_p_flag, proj_info[1]]).decode('utf-8', 'replace')

    targets, build_configs, schemes = parse_xcodebuild_list(output)

    args_passed = []
    if possible_args.configuration in build_configs:
        args_passed.append('-configuration')
        args_passed.append(possible_args.configuration)

    if possible_args.scheme in schemes:
        args_passed.append('-scheme')
        args_passed.append(possible_args.scheme)
    elif workspace and schemes:
        args_passed.append('-scheme')
        args_passed.append(schemes[0])

    if possible_args.target in targets:
        args_passed.append('-target')
        args_passed.append(possible_args.target)

    if possible_args.sdk:
        args_passed.append('-sdk')
        args_passed.append(possible_args.sdk)

    command = ['xcodebuild',
               "SYMROOT=build",
               w_or_p_flag, proj_info[1]] + args_passed

    run_build(command, possible_args.verbose, project)


def build_project_or_workspace(project, args):
    """Try to build the workspace or project specified via command-line arguments, passing on
    any arguments provided. Otherwise try to build the first scheme for the first workspace found,
    and if there isn't a workspace, the first project."""
    chdir('./' + project.folder) #project and zip file are in here

    if project.project_files:
        project_names_and_locs = {search(r'/(.+).xcodeproj$', name).groups()[0]: name
                                  for name in project.project_files}

    if project.workspace_files:
        workspace_names_and_locs = {search(r'/(.+).xcworkspace$', name, UNICODE).groups()[0]: name
                                    for name in project.workspace_files}
        if args.workspace and args.workspace in workspace_names_and_locs.keys(): # workspace arg
            setup_build(workspace_names_and_locs[args.workspace], args, workspace=True)
        elif args.project and args.project in project_names_and_locs.keys(): # project arg
            setup_build(project_names_and_locs[args.project], args)
        else:
            setup_build(project.workspace_files[0], args, workspace=True) # first workspace
    elif project.project_files:
        if args.project and args.project in project_names_and_locs.keys(): # project arg
            setup_build(project_names_and_locs[args.project], args)
        else:
            setup_build(project.project_files[0], args) # first project
