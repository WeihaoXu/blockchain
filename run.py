import subprocess
from subprocess import Popen

if __name__ == '__main__':
    ports = "\"5000 5001 5002 5003 5004\""
    port_nums = [5000, 5001, 5002, 5003, 5004]
    commands = []
    for port in port_nums:
        commands.append('python app.py {} {}'.format(port, ports))


    # run in parallel
    processes = [Popen(cmd, shell=True) for cmd in commands]
    # do other things here..
    # wait for completion
    for p in processes: p.wait() 




