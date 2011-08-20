import sys
import os
import socket

def system_info():
    '''get some basic system information'''
    results = {}
    results['platform'] = sys.platform
    results['version_info'] = sys.version_info
    results['pythonpath'] = sys.path
    results['path'] = os.getenv('PATH')
    results['hostname'] = socket.gethostname()
    results['fqdn'] = socket.getfqdn()
    results['ip'] = socket.gethostbyname(socket.getfqdn())
    return results

if __name__ == '__channelexec__':
    results = system_info()
    channel.send(results)

if __name__ == '__main__':
    results = system_info()
    print results

