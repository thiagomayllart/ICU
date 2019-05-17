import subprocess
import psutil
# Iterate over all running process
def kill_process_like(command):
    ps = subprocess.Popen(['ps', 'aux'], stdout=subprocess.PIPE).communicate()[0]
    processes = ps.split('\n')
    for row in processes[1:]:
        descrpt = row.split(None, 10)
        if command in descrpt[10]:
            p = psutil.Process(int(descrpt[1]))
            p.terminate()
            print "Killed SSH process"
            break


def is_scan_running():
    ps = subprocess.Popen(['ps', 'aux'], stdout=subprocess.PIPE).communicate()[0]
    processes = ps.split('\n')
    for row in processes[1:]:
        descrpt = row.split(None, 10)
        if len(descrpt) == 10:
            if "run.py" in descrpt[10]:
                return True

    return False
