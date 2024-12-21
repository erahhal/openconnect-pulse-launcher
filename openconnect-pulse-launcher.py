#!/usr/bin/env python

import getopt
import inspect
import logging
import os
import psutil
import signal
import shutil
import subprocess
import sys
import time
import urllib

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from xdg_base_dirs import xdg_config_home

script_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

class OpenconnectPulseLauncher:

    def signal_handler(self, _sig, _frame):
        subprocess.run(['sudo', 'route', 'del', 'default', 'gw', self.vpn_gateway_ip])
        while 'openconnect' in (i.name() for i in psutil.process_iter()):
            subprocess.run(['sudo', 'pkill', 'openconnect'])
        ps = subprocess.Popen(
            ['getent', 'hosts', self.hostname],
            stdout=subprocess.PIPE,
        )
        output = subprocess.check_output(
            ['awk', '{print $1}'],
            stdin=ps.stdout
        )
        ps.wait()
        vpn_ip = output.decode().rstrip()
        # This is normally deleted when the VPN is killed, but sometimes is left behind as there are two entries
        subprocess.run(['sudo', 'route', 'del', vpn_ip])
        sys.exit(0)

    def init(self):
        self.is_root = os.geteuid() == 0
        self.chrome_profile_dir = os.path.join(xdg_config_home(), 'chromedriver', 'pulsevpn')
        if not os.path.exists(self.chrome_profile_dir):
            os.makedirs(self.chrome_profile_dir)
        config_dir = os.path.join(xdg_config_home(), 'openconnect-pulsevpn')
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

        self.cookie_file = os.path.join(config_dir, 'cookie.txt')
        cookie = None
        if os.path.isfile(self.cookie_file):
          cookie_file_handle = open(self.cookie_file, 'r')
          cookie = cookie_file_handle.read()
          cookie_file_handle.close()

        self.vpn_gateway_ip = None

        signal.signal(signal.SIGINT, self.signal_handler)

    def is_dsid_valid(self, dsid):
        # Expiry is set to Session
        return dsid is not None and 'value' in dsid

    def connect(self, vpn_url, chromedriver_path, chromium_path, debug=False, script=None):
        self.hostname = urllib.parse.urlparse(vpn_url).hostname

        dsid = None
        returncode = 0
        while True:
            if self.is_dsid_valid(dsid) and returncode != 2:
                logging.info('Launching openconnect.')

                ## Run in background

                ## openconnect is built to already point to a pre-packaged vpnc-script, so no need to specify
                # p = subprocess.run(['sudo', 'openconnect', '-b', '-C', dsid['value'], '--protocol=pulse', vpn_url, '-s', '${pkgs.unstable.vpnc-scripts}/bin/vpnc-script'])

                ## --no-dtls addresses VPN dying with "ESP detected dead peer", and also "ESP receive error: Message too long" error
                ## See: https://gitlab.com/openconnect/openconnect/-/issues/647
                ## Downside: lots of console spam
                ## Also, seems to die often with this error:
                ##    Short packet received (2 bytes)
                ##    Unrecoverable I/O error; exiting.
                # p = subprocess.run(['sudo', 'openconnect', '--no-dtls', '-b', '-C', dsid['value'], '--protocol=pulse', vpn_url])
                command_line = ['sudo', 'openconnect']
                if debug:
                    command_line.extend(['-vvvv'])
                if script is not None:
                    command_line.extend(['-s', script])
                command_line.extend(['-b', '-C', dsid['value'], '--protocol=pulse', vpn_url])
                if debug:
                    print('Command line:')
                    print('    {}'.format(' '.join(command_line)))
                    print('')
                p = subprocess.run(command_line)

                returncode = p.returncode

                ## Get tun0 IP and set as default GW (vpnc-script doesn't do this for some reason)
                ## Probably due to something like this:
                ## https://github.com/dlenski/openconnect/issues/125#issuecomment-426032102
                ## There is an error on the command line when openconnect is run:
                ## Error: argument "via" is wrong: use nexthop syntax to specify multiple via

                ## sleep to make sure tun0 is available
                time.sleep(3)
                ps = subprocess.Popen(
                  ['ifconfig', 'tun0'],
                  stdout=subprocess.PIPE
                )
                output = subprocess.check_output(
                  ['awk', '-F', ' *|:', '/inet /{print $3}'],
                  stdin=ps.stdout
                )
                ps.wait()
                self.vpn_gateway_ip = output.decode().rstrip()
                print('VPN IP: '+self.vpn_gateway_ip)
                p = subprocess.run(['sudo', 'route', 'add', 'default', 'gw', self.vpn_gateway_ip])

                # Wait for ctrl-c
                signal.pause()
            else:
                returncode = 0
                service = Service(executable_path=chromedriver_path)
                options = webdriver.ChromeOptions()
                options.binary_location = chromium_path
                options.add_argument('--window-size=800,900')
                # options.add_argument('--remote-debugging-pipe')
                # options.add_argument('--remote-debugging-port=9222')
                options.add_argument('user-data-dir=' + self.chrome_profile_dir)

                logging.info('Starting browser.')
                driver = webdriver.Chrome(service=service, options=options)

                wait = WebDriverWait(driver, 60)
                driver.get(vpn_url)
                dsid = wait.until(lambda driver: driver.get_cookie('DSID'))
                driver.quit()
                if self.is_dsid_valid(dsid):
                    cookie_file_handle = open(self.cookie_file, 'w')
                    cookie = cookie_file_handle.write(dsid['value'])
                    cookie_file_handle.close()

                logging.info('DSID cookie: %s', dsid)

def main(argv):
    script_name = os.path.basename(__file__)
    chromedriver_path = shutil.which('chromedriver')
    chromium_path = shutil.which('chromium') or shutil.which('google-chrome')
    help_message = '{} <vpn_url>'.format(script_name)

    try:
        opts, args = getopt.getopt(argv, 'hds:c:', ['help', 'debug', 'script=', 'chromedriver-path'])
    except getopt.GetoptError:
        print(help_message)
        sys.exit(2)
    if len(args) != 1:
        print(help_message)
        sys.exit(2)
    debug = False
    script = None
    for o, a in opts:
        if o in ('-h', '--help'):
            print(help_message)
            sys.exit()
        elif o in ('-d', '--debug'):
            debug = True
        elif o in ('-s', '--script'):
            if len(a):
                script = a
        elif o in ('-c', '--chromedriver-path'):
            if len(a):
                chromedriver_path = a
    vpn_url = args[0]

    launcher = OpenconnectPulseLauncher()
    launcher.init()
    launcher.connect(vpn_url, chromedriver_path=chromedriver_path, chromium_path=chromium_path, debug=debug, script=script)

if __name__ == "__main__":
    main(sys.argv[1:])
