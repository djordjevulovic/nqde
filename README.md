# NSO Quick Development Environment (NQDE)

## Running NQDE commands

NQDE commands are implemented as roles of the Ansible playbook. There are two ways to run these commands:
- Using provided Ansible "run_role" playbook


- Using provided "run_playbook.py" Python script

usage: run_playbook.py [-h] [--root ROOT] --playbook PLAYBOOK
                       [--include INCLUDE] [--extra_var EXTRA_VAR] [--verbose]

optional arguments:
  -h, --help            show this help message and exit
  --root ROOT, -r ROOT  Root NQDE directory
  --playbook PLAYBOOK, -p PLAYBOOK
                        Playbook name (without .yml)
  --include INCLUDE, -i INCLUDE
                        YAML var file to be included
  --extra_var EXTRA_VAR, -e EXTRA_VAR
                        Variable (key=value) to be included
  --verbose, -v         Verbose output

## Installing NSO Software
  
### Installing NSO Binaries

1. Copy NSO binary file (ending with *.bin) into "nso-bin" directory
2. From the NQDE top level directory run command "ansible-playbook playbooks/unpack_nso.yml"
 
### Installing NEDs

1. Copy NED binary file (ending with *.bin) into "nso-neds" directory
2. From the NQDE top level directory run command "./unpack_all.sh"
 
## Create New NQDE Project

### Create Project Skeleton

1. From the NQDE projects directory run command "./create_project_skeleton.sh \<project name\>"

### Customize Project Skeleton

1. Edit default project config files:
 - project/\<project name\>/\<project name\>_runtime.yml
 - project/\<project name\>/\<project name\>_packages.yml
 - project/\<project name\>/\<project name\>_devices.yml

### Create Project Packages

1. From the project directory run command "./create_project_packages.sh"

### Create Project Run-time Environment

1. From the NQDE top level directory run command "ansible-playbook playbooks/create_project_runtime.yml -e "@projects/\<project name\>/\<projectname\>.yml"


### 