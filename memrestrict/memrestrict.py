import win32api
import win32security
import win32job
import win32con
import win32ras

# Note: based on example from - http://www.programcreek.com/python/example/4216/win32api.GetCurrentProcess
def AdjustPrivilege(priv, enable=1):
    # Get the process token
    flags = win32security.TOKEN_ADJUST_PRIVILEGES | win32security.TOKEN_QUERY
    htoken = win32security.OpenProcessToken(win32api.GetCurrentProcess(), flags)
    # Get the ID for the system shutdown privilege.
    idd = win32security.LookupPrivilegeValue(None, priv)
    # Now obtain the privilege for this process.
    # Create a list of the privileges to be added.
    if enable:
        newPrivileges = [(idd, win32security.SE_PRIVILEGE_ENABLED)]
    else:
        newPrivileges = [(idd, 0)]
    # and make the adjustment
    win32security.AdjustTokenPrivileges(htoken, 0, newPrivileges)


def main():
    argc = len(sys.argv)
    if argc != 2:
        print "Invalid command line argument"
        return 

    AdjustPrivilege(win32security.SE_DEBUG_NAME, 1)

    targetProcessId = sys.argv[1]
    hProcess = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_SET_QUOTA | win32con.PROCESS_TERMINATE, False, int(targetProcessId))
    if not win32ras.IsHandleValid(hProcess):
        print "Cannot retrieve handle of target process"
        return

    if win32job.IsProcessInJob(hProcess, None):
        print "Target process is already assigned to the job-object"
        return

    job = win32job.CreateJobObject(None, "MemRestrictedJob")
    if not win32ras.IsHandleValid(job):
        print "Cannot create job-object"
        return

    extLimitInfo = win32job.QueryInformationJobObject(job, win32job.JobObjectExtendedLimitInformation)
    extLimitInfo["ProcessMemoryLimit"] = 300*1024*1024
    extLimitInfo["BasicLimitInformation"]["LimitFlags"] = win32job.JOB_OBJECT_LIMIT_PROCESS_MEMORY
     
    win32job.SetInformationJobObject(job, win32job.JobObjectExtendedLimitInformation, extLimitInfo)

    win32job.AssignProcessToJobObject(job, hProcess)
    
    win32api.CloseHandle(job)

    print "Done"


if __name__ == "__main__":
  	main()