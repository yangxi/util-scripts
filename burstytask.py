import sys, os, time

def read_stat_line(stat_file):
    with open(stat_file, 'r') as f:
        return f.readline()

def get_uk_time(stat_line):    
    stats = stat_line.strip().split(' ')    
    utime = int(stats[13]) * 10
    ktime = int(stats[14]) * 10
    ret = [utime + ktime, utime, ktime]
    return ret

def process_thread_stat(process, tickCycle):
    threads = process["threads"]
    for t in threads:
        curr_ku = get_uk_time(threads[t]["curr_stat"]["stat"])
        last_ku = get_uk_time(threads[t]["last_stat"]["stat"])
        diff_ku = [curr_ku[0] - last_ku[0], curr_ku[1] - last_ku[1], curr_ku[2] - last_ku[2]]
        threads[t]["ticks"][tickCycle] = diff_ku    
                
def read_threads_stat(process):    
    process["last_sample"] = time.time() * 1000
    threads = process["threads"]
    for t in process["threads"]:
        now = time.time() * 1000
        stat_line = read_stat_line(threads[t]["stat_path"])
        threads[t]["curr_stat"] = {"stamp":now, "stat": stat_line}
    process["last_sample_end"] = time.time() * 1000
def swap_thread_stat(process):
    threads = process["threads"]
    for t in process["threads"]:
        threads[t]["last_stat"] = threads[t]['curr_stat']
def report_busies_tick(process):
    total_ticks = process["threads"]["pid"]["ticks"]
    pid = process["pid"]
    pid_name = process["name"]
    threads = process["threads"]
    busies_tick = 0
    total_time = -1
    for i in range(0, len(total_ticks)):
        this_tick = total_ticks[i]
        this_total_time = this_tick[0]
        if this_total_time > total_time:
            total_time = this_total_time
            busies_tick = i
    # "tick  total:totalu:totalk [tidTotal:tidu:tidk]"
    l = "****The bueiest tick: %d\t**********************\n"%(busies_tick)
    total_b_tick = total_ticks[busies_tick]
    l += "====Total pid (name): totalTime(ms), user, kernel===\n"
    l += "%s(%s): %.2f, %.2f, %.2f\n"%(pid, pid_name, total_b_tick[0], total_b_tick[1], total_b_tick[2])
    l += "====Threads tid (name): totalTime, user, kernel=====\n"
    for t in process["tids"]:
        thread_b_tick = threads[t]["ticks"][busies_tick]
        thread_id = threads[t]["tid"]
        thread_name = threads[t]["name"]
        if thread_b_tick[0] > 0:
            l += "%s(%s): %.2f, %.2f, %.2f\n" % (thread_id, thread_name, thread_b_tick[0], thread_b_tick[1], thread_b_tick[2])
    print(l)
def observe_process(process, tick, reportTick):
    threads = process["threads"]
    for t in threads:
        threads[t]["ticks"] = []
        for i in range(0, reportTick):
            threads[t]["ticks"].append([])
    read_threads_stat(process)
    swap_thread_stat(process)
    nr_tick = 0
    while(True):
        swap_thread_stat(process)
        nthTick = nr_tick % reportTick
        next_tick = process["last_sample"] + tick
        now = time.time() * 1000
        if next_tick > now:
            #print("sleep %dMS" % (next_tick - now))
            time.sleep((next_tick - now)/1000)
        read_threads_stat(process)
        process_thread_stat(process, nthTick)        
        nr_tick += 1
        if (nr_tick % reportTick == 0):
            report_busies_tick(process)

def observe(pid, tick, reportTick):        
    if not os.path.isdir("/proc/%s" % pid):
        print("proc/%s does not exist" % pid)
        return    
    pid_stat = open("/proc/%s/stat" % pid, 'r')
    pid_task_dir="/proc/%s/task" % pid
    threads_ids=os.listdir(pid_task_dir)
    print("%s has %d tasks");
    process = {"tids":threads_ids}
    threads = {}
    with open("/proc/%s/comm" % (pid), 'r') as comm_f:
            process_name = comm_f.readline().rstrip('\n')
            process_stat_path = '/proc/%s/stat' % (pid)         
            print("%s %s" % (pid, str(get_uk_time(read_stat_line(process_stat_path)))))
            process["pid"]=pid
            process["stat_path"]=process_stat_path
            process["name"]=process_name
            for i in threads_ids:
                with open("/proc/%s/task/%s/comm" % (pid, i), 'r') as comm_f:
                    thread_name = comm_f.readline().rstrip('\n')
                    thread_stat_path = '/proc/%s/task/%s/stat' % (pid, i)
                    thread_stat = read_stat_line(thread_stat_path)
                    print("%s %s %s" % (i, thread_name, str(get_uk_time(thread_stat))))
                    threads[i] = {"name": thread_name, "tid": i, "stat_path": thread_stat_path}
            threads["pid"] ={"name":process_name, "tid":pid, "stat_path": process_stat_path}
    process["threads"] = threads
    observe_process(process, tick, reportTick)
    

    pid_stat_f = open(pid_stat,'r')
    # for i in range(0, 1000):
    #     now = time.time();
    #     l = pid_stat_f.readline()
    #     then = time.time();
    #     print("%.3f %s" %((then-now)*1000, l))

if __name__ == "__main__":
    usage="burstytask.py PID sampling_tick(ms) report_period(report the busiest tick in N sampling ticks)"
    if len(sys.argv) < 2:
        print("Missing the target\nUsage:%s"%(usage))
        exit(1)
    pid = sys.argv[1]
    tick = 100
    period = 10
    if len(sys.argv) > 2:
        tick = int(sys.argv[2])
    if len(sys.argv) > 3:
        period = int(sys.argv[3])
    print("Observer proess %s every %dms report every %d ticks" % (pid, tick, period))
    observe(pid, tick, period)

        