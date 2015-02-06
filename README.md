# aws-ssh-client

This script is to automate finding proper instances on AWS Amazon Cloud and executing desired commands
Mostly created for System Administrators.

First version uploaded here is the 0.5 that already has few feautures that I've been working on.

CHANGELOG
  0.1 - initial version
  0.2 - Added host key policy check to alter know_hosts file with proper entires
  0.3 - Rewrite options to argparse and added Verbose
  0.4 - Added Host pattern to specify set of desired hosts tonnect
  0.5 - Added OpenSSH identity file handling. Moved options from class init into ss_cmd for better reuse in other scripts

REQUIREMENTS
  Python 2.6 or higher (not tested with python3)
  Paramiko python library
  Boto.ec2 python library
  AWS connfiguration in /etc/boto.cfg (Key + Secret)
