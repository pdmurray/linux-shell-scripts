#!/usr/bin/python

##############################################
# update_enom.py 
# Original version by: Sean Schertell, DataFly.Net
# Modifed by: Patrick Murray
# ------------------------
# A simple python script to update your dynamic DNS IP for domains registered with Enom.
# 
# Requirements:
# - You have a domain registered with Enom, nameservers are set to Enom's, and you've set a domain password
# - Your client machine runs python
# - You know how to configure a cron job to periodically run this script (every 5 mins recommended)
#
# Cron example to run every 5 minutes:
# */5 * * * * /usr/local/bin/update_enom.py


##############################################
# Configure
##############################################

ip_check_url = 'http://www.canyouseeme.org/'         # URL which returns current IP as text only
ip_text_file = '/usr/local/etc/update_enom.txt'      # Text file to store recent ip file
domain       = <domain name>                         # Enom registered domain to be altered
password     = <password>                            # Domain password

##############################################

import urllib2, re, os, time, datetime

def read_url(url):
    return urllib2.urlopen(url).read()

def read_current_ip(url):
    f = urllib2.urlopen(url)
    html_doc = f.read()
    f.close()
    m = re.search('(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)',html_doc)
    return m.group(0)
	
def read_file(path):
    return open(path, 'r').read()

def parse_enom_response(enom_response):
    enom_response_dict = {}
    for param in  enom_response.split('\n'):
        if '=' in param:
            try:
                key, val = param.split('=')
                enom_response_dict[key] = val.strip()
            except: pass
    return enom_response_dict

def save_new_ip(current_ip):
    return open(ip_text_file, 'w').write(current_ip)






def update_enom():   

    # Get the current time
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
 
    # First, ensure that the ip_text_file exists
    if not os.path.exists(ip_text_file):
        open(ip_text_file, 'w').close() 

    # Compare our recently saved IP to our current real IP
    recent_ip = read_file(ip_text_file)
    current_ip = read_current_ip(ip_check_url)

    # Do they match?
    if recent_ip == current_ip:
        print st + ": Last: " + str(recent_ip) + " Current: " + str(current_ip) + " - No update needed." 
        return # IP address has not changed since last update



    # No match, so let's try to update Enom


    # Read the current host list
    settings = {'domain': domain, 'password': password, 'current_ip': current_ip}
    updatestringbase = 'https://dynamic.name-services.com/interface.asp?command=SetDNSHost&zone=%(domain)s&DomainPassword=%(password)s' % settings


    hosts = {'home':'A'}

    # Build the rest of the update string
    for key in hosts:
        hostline = '&HostName={0}&RecordType={1}&Address={2}'.format(key, hosts[key], current_ip)
        updatestring = updatestringbase + hostline
        enom_response = read_url(updatestring)

        # Any errors?
        response_vals = parse_enom_response(enom_response)

        if not response_vals['ErrCount'] == '0':    
            raise Exception('*** FAILED TO UPDATE! Here is the response from Enom:\n' + enom_response)



    # Okay then, lets save the new ip
    save_new_ip(current_ip)
    print st + ": Last: " + str(recent_ip) + " Current: " + str(current_ip) + " - Successfully updated with enom." 
    return    
##############################################

update_enom()


