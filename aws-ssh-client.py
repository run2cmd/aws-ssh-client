#!/usr/bin/python26
'''
Script Name:     aws-ssh-client.py

Author:          run2cmd

Requirements:    Python 2.6 or higher (not tested with python3)
                 Paramiko python library
                 Boto.ec2 python library
                 AWS connfiguration in /etc/boto.cfg (Key + Secret)

Version:         0.1 - initial version
                 0.2 - Added host key policy check to alter know_hosts file with proper entires
                 0.3 - Rewrite options to argparse and added Verbose
                 0.4 - Added Host pattern to specify set of desired hosts to connect
                 0.5 - Added OpenSSH identity file handling. Moved options from class init into ss_cmd for better reuse in other scripts
'''

import paramiko
import getpass
import os
import boto.ec2
import socket
import argparse


class RunCommands():

    def __init__(self):
        self.ec2_conn = boto.ec2.connect_to_region('eu-west-1')
        self.ec2_all_instances = self.ec2_conn.get_all_instances()
        self.all_hosts = []
        if o_key == '':
            self.mypass = getpass.getpass('Password: ')

    def ssh_cmd(self, host_n, user_name, cmd, key_file=''):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if key_file != '':
            client.connect(host_n, username=user_name, key_filename=key_file)
        else:
            client.connect(host_n, username=user_name, password=self.mypass)
        stdin, stdout, stderr = client.exec_command(cmd)
        for line in stdout:
            print '\t' + line.strip('\n')
        for line in stderr:
            print '\t' + line.strip('\n')
        client.close()

    def get_hosts(self, name_pattern):
        for host in self.ec2_all_instances:
            for host_atr in host.instances:
                if 'terminated' in str(host_atr._state) or 'stopped' in str(host_atr._state) or 'Name' not in host_atr.tags:
                    pass
                else:
                    if name_pattern == 'all':
                        self.all_hosts.append({'IP': host_atr.private_ip_address, 'State': str(host_atr._state), 'Name': host_atr.tags['Name']})
                    else:
                        if self.name in host_atr.tags['Name']:
                            self.all_hosts.append({'IP': host_atr.private_ip_address, 'State': str(host_atr._state), 'Name': host_atr.tags['Name']})
        return self.all_hosts


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='This is automated ssh tool for ssh using LDAP passords.\nCreated by Piotr.Bugala@acxiom.com.')
    parser.add_argument('-u', type=str, help='Username', required=True)
    parser.add_argument('-c', type=str, help='Command to execute. You can use quotes and double quotes', required=True)
    parser.add_argument('-v', type=int, help='Verbose mode', default=0)
    parser.add_argument('-n', type=str, help='Host Name Pattern', default='all')
    parser.add_argument('-i', type=str, help='Path to OpenSSH key file', default='')
    args = parser.parse_args()
    o_user = args.u
    o_cmd = args.c
    o_verbose = args.v
    o_pattern = args.n
    o_key = args.i

    rcmd = RunCommands()
    all_hosts = rcmd.get_hosts(o_pattern)
    failed_hosts = []

    for ec2_host in all_hosts:
        if 'running' in ec2_host['State']:
            try:
                if o_verbose == 1:
                    print ec2_host['Name']
                if o_key != '':
                    rcmd.ssh_cmd(ec2_host['IP'], o_user, o_cmd, key_file=o_key)
                else:
                    rcmd.ssh_cmd(ec2_host['IP'], o_user, o_cmd)
            except (paramiko.BadAuthenticationType):
                failed_hosts.append({'Name': ec2_host['Name'], 'IP': ec2_host['IP'], 'Code': 'Failed to authenticate'})
                pass
            except (paramiko.AuthenticationException):
                failed_hosts.append({'Name': ec2_host['Name'], 'IP': ec2_host['IP'], 'Code': 'Failed to login'})
                pass
            except (socket.error):
                failed_hosts.append({'Name': ec2_host['Name'], 'IP': ec2_host['IP'], 'Code': 'Failed to connect'})
                pass

    print '\n\nFailed command on following hosts:' 
    for f_host in failed_hosts:
        print "%s (%s) - %s" % (f_host['Name'], f_host['IP'], f_host['Code'])
