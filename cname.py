import sys
import queue
import threading

import dns.resolver
from dns.rcode import to_text
from dns.exception import DNSException
from colorama import Fore, init

#enable coloring on win
try:
	import win_unicode_console
	win_unicode_console.enable()
	init()
except ImportError:
	pass


#queue and lock var
domains = queue.Queue()
lock = threading.Lock()

# reading args
try:
	sublist = sys.argv[1]
except IndexError:
	sublist = ""

# reading file
try:
	subfile = open(sublist, 'r')
except IOError:
	subfile = sublist.split(",")

# setting dns resolver
my_resolver = dns.resolver.Resolver()
my_resolver.nameservers = ['8.8.8.8']

# populate queue with domains
for sub in subfile:
	domains.put(sub.strip())

try:
	subfile.close()
except AttributeError:
	pass

# checking cname
def Check(domain):
	try:
		answer = my_resolver.resolve(domain, 'CNAME')
		for data in answer:
			with lock:
				cname_string = str(data.target).rstrip(".")
				#cname_error = to_text(answer.response.rcode()).lower()
				print("{0:30}{1} -->\t {2}{3}".format(domain, Fore.LIGHTBLUE_EX, Fore.RESET, cname_string))
	except DNSException:
		pass
	domains.task_done()

# starting threads
while not domains.empty():
	domain = domains.get()
	try:
		threading.Thread(target=Check,args=(domain,)).start()
	# avoid thread start error
	except RuntimeError:
		domains.task_done()
		domains.put(domain)

# wait until all threads done
domains.join()
