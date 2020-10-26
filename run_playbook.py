import os
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.module_utils.common.collections import ImmutableDict
from ansible import context
from ansible.utils.vars import load_extra_vars
from  ansible.plugins.callback import CallbackBase
from datetime import datetime
import logging
import argparse

class NQDE_Ansible_Callback(CallbackBase):
    """Sample callback"""

    def __init__(self):
        super(NQDE_Ansible_Callback, self).__init__()
        # store all results
        self.results = []
        self.start_time = datetime.now()

    def v2_runner_on_ok(self, result, **kwargs):
        """Save result"""
        self.results.append(result)

        logging.info("Host {} Play {} OK".format(result._host, result.task_name))

        if 'ansible_facts' in result._result:
            for key, value in result._result['ansible_facts'].items():
                logging.debug("Set fact {} to {}".format(key, value))

#        else:
#            logging.debug("{}".format(result._result))

    def v2_runner_on_failed(self, result, ignore_errors=False):

        logging.debug("RAW Play FAILED: {}".format(result._result))

        if 'results' in result._result:
            for e in result._result['results']:
                if 'failed' in e and e['failed'] is True:
                    logging.debug("info {} Play {} FAILED: {}".format(result._host, result.task_name, e['msg']))
        else:
            logging.debug("Host {} Play {} FAILED: {}".format(result._host, result.task_name, result._result['msg']))

    def v2_playbook_on_stats(self, stats):
        run_time = datetime.now() - self.start_time
        self.runtime = run_time.seconds  # returns an int, unlike run_time.total_seconds()

        hosts = sorted(stats.processed.keys())
        for h in hosts:
            t = stats.summarize(h)

            msg = "PLAY RECAP [%s] : %s %s %s %s %s" % (
                h,
                "ok: %s" % (t['ok']),
                "changed: %s" % (t['changed']),
                "unreachable: %s" % (t['unreachable']),
                "skipped: %s" % (t['skipped']),
                "failed: %s" % (t['failures']),
            )

            logging.debug(msg)
#            self.logger.append(msg)

class NQDE_Ansible():

    def __init__(self, root_dir = None):

        self.global_loader = DataLoader()
        self.global_inventory = InventoryManager(loader=self.global_loader)
        # sources='/home/ansible/nso2_ipconnect_ansible/nso2_lab_hosts.yml')

        if root_dir is None:
            self.root_dir = os.getcwd()
        else:
            self.root_dir = root_dir

#        self.playbook_path = '/home/ansible/nso2_ipconnect_ansible/ipconnect.yml'

    def run_playbook(self, playbook_name, include_set = set()):

#        current_dir = os.getcwd()

        playbook_file = self.root_dir + "/playbooks/" + playbook_name + ".yml"

        if not os.path.exists(playbook_file):
            logging.error("Playbook {} not found".format(playbook_file))
            return False

        logging.info('Runnning playbook {}'.format(playbook_file))
        logging.info('Including var files {}'.format(include_set))

        context.CLIARGS = ImmutableDict(connection='local',
                                        forks=10,
                                        become=None,
                                        become_method=None,
                                        become_user=None,
                                        check=False,
                                        diff=False,
                                        syntax=False,
                                        start_at_task=None,
                                        verbosity=True,
                                        extra_vars=include_set
                                        )
# ={'dry_run=True', 'service_file={}'.format(service_file)

        variable_manager = VariableManager(loader=self.global_loader,
                                           inventory=self.global_inventory)

#        self.global_variable_manager.extra_vars['dry_run'] = "True"

        pbex = PlaybookExecutor(playbooks=[playbook_file],
                                    variable_manager=variable_manager,
                                    loader=self.global_loader,
                                    inventory=self.global_inventory,
                                    passwords={})

        results_callback = NQDE_Ansible_Callback()
        pbex._tqm._stdout_callback = results_callback
        return_code = pbex.run()
        results = results_callback.results

        logging.debug("return code = " + str(return_code))

        if return_code == 0:
            logging.info("Playbook successfully finished")

        return True

parser = argparse.ArgumentParser()
parser.add_argument('--root', '-r', help="Root NQDE directory", required=False)
parser.add_argument('--playbook', '-p', help="Playbook name (without .yml)", required=True)
parser.add_argument('--include', '-i', action='append', help="YAML var file to be included")
parser.add_argument('--extra_var', '-e', action='append', help="Variable (key=value) to be included")
parser.add_argument('--verbose', '-v', help="Verbose output", action="store_true")

args = parser.parse_args()

if args.verbose is True:
  logging.basicConfig(level=logging.DEBUG)


#print(list)

runner = NQDE_Ansible(args.root if args.root else None)
include_set =  { "@"+file  for file in args.include } if args.include else set()
runner.run_playbook(args.playbook, include_set)
