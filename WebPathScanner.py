from multiprocessing import Pool,Value,Lock
import requests
import timeit
import signal
import sys
import re
import os
from colorama import Fore,Back,Style


URL = ''
default_payload = 'payloads/default-payload'
user_payload = ''
count = 0
args = sys.argv
progress = Value('i',0)  # shared variable
filter_statusCode = 0
output_path = ''

# logo
print(Fore.LIGHTGREEN_EX + '''
 __          __  _     _____      _   _      _____                                 
 \ \        / / | |   |  __ \    | | | |    / ____|                                
  \ \  /\  / /__| |__ | |__) |_ _| |_| |__ | (___   ___ __ _ _ __  _ __   ___ _ __ 
   \ \/  \/ / _ \ '_ \|  ___/ _` | __| '_ \ \___ \ / __/ _` | '_ \| '_ \ / _ \ '__|
    \  /\  /  __/ |_) | |  | (_| | |_| | | |____) | (_| (_| | | | | | | |  __/ |   
     \/  \/ \___|_.__/|_|   \__,_|\__|_| |_|_____/ \___\__,_|_| |_|_| |_|\___|_|   
''' + Style.RESET_ALL)
print('Coded by: ' + Fore.LIGHTCYAN_EX + 'm-alaiady\t\t\t\t\t\t\t\t' + Style.RESET_ALL + Fore.LIGHTYELLOW_EX + 'v1.0' + Style.RESET_ALL + '\n')

# counting the payloads
#for line in open(payload_path): count += 1

def counting_payloads(payload_path):
  global count
  if payload_checker(payload_path):
    for line in open(payload_path): count += 1
  else:
    print('[!] WebPathScanner didn\'t find the payload!')
    sys.exit(1)

def payload_checker(payload_path):
  if os.path.exists(payload_path):
    return True
  else:
    return False

def options():
  global URL
  global filter_statusCode
  global output_path
  global user_payload
  option = 0
  for i in args[1:]:
    option = option + 1
    if i == '-u':
      try:
        URL = args[option + 1]
      except:
        print('[' + Fore.RED + 'FATAL' + Style.RESET_ALL + ']' + ' Please provide a URL\n')
        sys.exit(1)
    elif i == '-p':
      try:
        user_payload = args[option + 1]
      except:
        print('[' + Fore.RED + 'FATAL' + Style.RESET_ALL + ']' + ' Please provide a payload path\n')
        sys.exit(1)
    elif i == '-c':
      try:
        filter_statusCode = args[option + 1]
      except:
        print('[' + Fore.RED + 'FATAL' + Style.RESET_ALL + ']' + ' -c flag need a value(int)')
        sys.exit(1)
    elif i == '-o':
      try:
        output_path = args[option + 1]
      except:
         print('[' + Fore.RED + 'FATAL' + Style.RESET_ALL + ']' + ' -o flag need a path to save the output')
         sys.exit(1)

def url_validator(URL):
  #if re.match("(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))",URL):
  if re.match(r"^http(s?):\/\/([A-Za-z0-9]\.|[A-Za-z0-9][A-Za-z0-9-]{0,61}[A-Za-z0-9]\.){1,3}[A-Za-z]{2,6}$",URL):
    return True
  else:
    return False

# function for calculating the processing time
def timer(number, repeat):
    def wrapper(func):
        runs = timeit.repeat(func, number=number, repeat=repeat)
        print('Time taken: {} s'.format(sum(runs) / len(runs)) )
        print(Fore.YELLOW + 'Visit' + Style.RESET_ALL + Fore.CYAN + ' https://github.com/m-alaiady' + Style.RESET_ALL + Fore.YELLOW + ' for more tools' + Style.RESET_ALL)
    return wrapper

def fetch(session,URL,status_code):
  lock = Lock()
  with session.get(URL) as response:
    with lock:
      global progress
      progress.value += 1
      if output_path == '':
        if status_code != 0:
          if response.status_code == int(status_code):
            print('[{}/{}] '.format(progress.value,count) + Fore.LIGHTMAGENTA_EX + '\t{}'.format(response.status_code) + Style.RESET_ALL + '\t\t\t\t{}'.format(response.url))
        else:
          if response.status_code == 404:
            print('[{}/{}] '.format(progress.value,count) + Fore.RED + '\t{}'.format(response.status_code) + Style.RESET_ALL + '\t\t\t\t{}'.format(response.url))
          elif response.status_code == 403:
            print('[{}/{}] '.format(progress.value,count) + Fore.CYAN + '\t{}'.format(response.status_code) + Style.RESET_ALL + '\t\t\t\t{}'.format(response.url))
          elif response.status_code == 302:
            print('[{}/{}] '.format(progress.value,count) + Fore.YELLOW + '\t{}'.format(response.status_code) + Style.RESET_ALL + '\t\t\t\t{}'.format(response.url))
          else:
            print('[{}/{}] '.format(progress.value,count) + Fore.WHITE + '\t{}'.format(response.status_code) + Style.RESET_ALL + '\t\t\t\t{}'.format(response.url))     
      else:
        if status_code != 0: # check if -c option is enabled
          if response.status_code == int(status_code):
            with open(output_path, 'a') as f:
              print('{}'.format(response.status_code) + '\t' + response.url , file=f)
        else:
           with open(output_path, 'a') as f:
            print('{}'.format(response.status_code) + '\t' + response.url , file=f)

def run(URL,status_code,payload_path):
  print('Progress\tStatus Code\t\t\tURL\n------------------------------------------------------------------------------------------')
  original_sigint_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
  with Pool() as pool:
    with requests.Session() as session:
      with open(payload_path) as payloads:
        signal.signal(signal.SIGINT,original_sigint_handler)
        try:
          pool.starmap(fetch, [(session,URL + '/' + payload,status_code) for payload in payloads] )
        except KeyboardInterrupt:
          print('\nWebPathScanner Quitting .. Bye ')
          pool.terminate()
        else:
          print('\nWebPathScanner Finished\n')

@timer(1,1)
def main():
  options()
  payload_path = ''
  if user_payload == '':
    counting_payloads(default_payload)
    payload_path = default_payload
    print(Fore.LIGHTMAGENTA_EX + "[~] WebPathScanner using the default payload" + Style.RESET_ALL)
  else:
    counting_payloads(user_payload)
    payload_path = user_payload
    print(Fore.LIGHTYELLOW_EX + "[~] WebPathScanner using the user payload" + Style.RESET_ALL)
  if URL != '':
    if url_validator(URL):
      try:
        timeout = 5
        request = requests.get(URL,timeout=timeout)
        run(URL,filter_statusCode,payload_path)
      except (requests.ConnectionError, requests.Timeout) as exception:
        print(Fore.RED + 'WebPathScanner did not find the target' + Style.RESET_ALL)
    else:
      print('[' + Fore.RED + 'FATAL' + Style.RESET_ALL + ']' + ' Please provide a valid URL')
      sys.exit(1)
  else:
    print('Usage: python3 WebPathScanner.py -u URL [<options>]\n\noptions:\n  -p select a specific payload\n  -c filter status code\n  -o save output to file\n  -h show this page\n')
    sys.exit(1)
