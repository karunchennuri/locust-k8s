"""
The entrypoint for the locust docker image.

:env LOCUST_MODE: One of 'standalone', 'master', or 'slave'.
:env LOCUST_FILE: String of the python locust file which will be used by locust.This string should include the
newlines.
Docker run command will probably include '-e LOCUST_FILE="$(cat locustfile.py)"'.
:env LOCUST_TARGET_HOST: The host to target; may be specified within the locustfile instead.
:env LOCUST_WEB_PORT: Port to host the locust interface on. Defaults to 80.
:env LOCUST_NO_WEB: One of 'true' or 'false'. Defaults to 'false'. If sets it will enable locust's no-web mode.
:env LOCUST_NUM_CLIENTS: Number of clients to simulate if in no-web mode.
:env LOCUST_HATCH_RATE: Hatch rate of simulated clients if in no-web mode.
:env LOCUST_SLAVE_COUNT: Number of connected salves to expect if in no-web mode.
:env LOCUST_MASTER_PORT: Port the master exposes for slave connection (will use MASTER_PORT and MASTER_PORT + 1).
:env LOCUST_MASTER: Host address of the master node.
"""

import os
import sys


def getenv(name: str) -> str:
    value = os.getenv(name)
    if not value:
        print('Please set the {} env var!'.format(name), file=sys.stderr)
        exit(1)
    return value


def write_locustfile():
    locust_file = getenv('LOCUST_FILE')
    with open('locustfile.py', 'w') as lfile:
        lfile.write(locust_file)


def common_args():
    web_port = getenv('LOCUST_WEB_PORT')
    args = ['-m', 'locust.main', '-P', web_port]
    if os.getenv('HOST'):
        args.extend(['-H', os.getenv('HOST')])
    return args


def no_web_args():
    args = []
    if getenv('LOCUST_NO_WEB').lower() == 'true':
        args = ['--no-web', '-r', getenv('LOCUST_HATCH_RATE'), '-c', getenv('LOCUST_NUM_CLIENTS')]
        if os.getenv('LOCUST_SLAVE_COUNT'):
            args.append('--expect-slaves={}'.format(os.getenv('LOCUST_SLAVE_COUNT')))
    return args


def singleton():
    args = common_args()
    args.extend(no_web_args())
    return args


def master():
    args = common_args()
    args.extend(no_web_args())
    args.append('--master')
    args.append('--master-bind-port={}'.format(getenv('LOCUST_MASTER_PORT')))
    return args


def slave():
    args = common_args()
    args.append('--slave')
    args.append('--master-host={}'.format(getenv('LOCUST_MASTER')))
    args.append('--master-port={}'.format(getenv('LOCUST_MASTER_PORT')))
    return args


def main():
    write_locustfile()
    
    mode = getenv('LOCUST_MODE').lower()
    args = {  # call appropriate function to get args
        'standalone': singleton,
        'master': master,
        'slave': slave
    }[mode]()

    os.system('echo "{}"'.format(args))  # print does not work due to the immediate exec
    os.execl(sys.executable, sys.executable, *args)


if __name__ == '__main__':
    main()
