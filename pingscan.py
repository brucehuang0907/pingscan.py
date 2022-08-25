import asyncio
import sys,time,re,os

CONCURRENT_LIMIT = 100
PING_COUNT = 4
WAIT_MS = 1000  #1000ms

async def asyncping(host):
    host = host.rstrip('\n')  # drop newline
    # print(f'Ping {host}...')
    if os.name == 'posix':
        count = '-c'
        wait = '-W'
    elif os.name == 'nt':
        count = '-n'
        wait = '-w'       
    proc = await asyncio.create_subprocess_shell(
        # powershell -n 4, macOS -c 4
        f'ping {count} {PING_COUNT} {wait} {WAIT_MS} {host}',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    # print(f'exited with {proc.returncode}')
    if stdout:
        # print(f"[stdout]\n{stdout.decode('utf-8')}")
        result = stdout.decode('utf-8')
        pk_ls,tm = '', ''
        for line in result.split('\n'):
            # parse stdout from macOS
            if 'packet loss' in line:
                s = line.split(',')[2]
                pk_ls = re.search('(\d{1,3}\.\d\%)',line)[0]
            if 'round-trip' in line:
                s =re.split('[ \/\=]',line)
                tm = f'{s[8]}{s[11]}'

            # parse stdout from powershell
            if 'Packets: Sent' in line:
                pk_ls = re.search('\d{1,3}%',line)[0].strip()
                # print(f'{host =} {pk_ls =}')
            if 'Minimum' in line:
                s =re.split(' \= ',line)
                tm = f'{s[3]}'.strip()
            if not tm:
                tm = '-'
        if '100' not in pk_ls:
            return pp(host,tm,pk_ls)
        else:
            return pp(host,"-",pk_ls)
    else:
        return pp(host,'error','error')

sem = asyncio.Semaphore(CONCURRENT_LIMIT)
async def safe_asyncping(host):
    async with sem:  # semaphore limits num of simultaneous downloads
        return await asyncping(host)

async def ping_segment(oct):

    tasks = [
        asyncio.ensure_future(safe_asyncping(f'{oct[0]}{i}'))  # creating task starts coroutine
        for i
        in range(int(oct[1]),int(oct[2])+1)
    ]
    await asyncio.gather(*tasks)  # await moment all downloads done

async def ping_list(host_list):

    tasks = [
        asyncio.ensure_future(safe_asyncping(f'{host}'))  # creating task starts coroutine
        for host
        in host_list
    ]
    await asyncio.gather(*tasks)  # await moment all downloads done

def pp(*input):
    print(f"{input[0]:<20} {input[1]:<10} {input[2]:<8}")
def lines_to_list(input):
    return [re.findall(r'[\s\;\,\"\']?([^\s\;\,\"\']+)[\s\;\,\"\']?',line.strip())[0] for line in input.strip().splitlines() if line]


if __name__ ==  '__main__':
    try:
        arg = sys.argv[1]
    except:
        arg = ""
    host_list=[]
    start = time.time()
    if not arg:
        print("You could paste a list of IP/hostname below for ping scan, end input with two Enters:")
        input_str=""
        while True:
            input_line = input()

            # if user pressed Enter without a value, break out of loop
            if input_line == '':
                break
            else:
                input_str += input_line + '\n'
        input_list = lines_to_list(input_str.strip())
        scan_subnet = False
    elif "-" in arg:
        scan_subnet = True
        oct = re.match('(\d{1,3}\.\d{1,3}\.\d{1,3}\.)(\d{1,3})[ \-]+(\d{1,3})$',arg).groups()
    start = time.time()
    if scan_subnet:
        print(f"started at {time.strftime('%X')}, ping {oct[0]}{oct[1]} - {oct[2]}:")
        print(f"{'ip':<15} {'time':<10} {'loss':<8}")
        if os.name == 'posix':
            loop = asyncio.get_event_loop()
        elif os.name == 'nt':
            loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(ping_segment(oct))
        finally:
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.close()
    else:
        print(f"started at {time.strftime('%X')}, ping a list of IP/host:")
        print(f"{'ip/host':<20} {'time':<10} {'loss':<8}")
        if os.name == 'posix':
            loop = asyncio.get_event_loop()
        elif os.name == 'nt':
            loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(ping_list(input_list))
        finally:
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.close()

    end = time.time()
    print(f"Completed in {(end - start):.2f}s")
