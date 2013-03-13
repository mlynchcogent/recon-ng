import framework
# unique to module
import os
import dns
import re

class Module(framework.module):

    def __init__(self, params):
        framework.module.__init__(self, params)
        self.register_option('nameserver', '', 'yes', 'ip address of target\'s nameserver')
        self.register_option('domains', './data/av_domains.lst', 'yes', 'domain or list of domains to snoop for')
        self.info = {
                     'Name': 'DNS Cache Snooper',
                     'Author': 'thrapt (thrapt@gmail.com)',
                     'Description': 'Uses the DNS cache snooping technique to check for visited domains',
                     'Comments': [
                                  'Nameserver must be in IP form.',
                                  'Source options: [ <domain> | ./path/to/file | query <sql> ]',
                                  'http://304geeks.blogspot.com/2013/01/dns-scraping-for-corporate-av-detection.html'
                                 ]
                     }

    def module_run(self):
        nameserver = self.options['nameserver']['value']
        
        domains = self.get_source(self.options['domains']['value'])
        if not domains: return

        self.output('Starting queries...')
        
        for domain in domains:
            response = None
            # prepare our query
            query = dns.message.make_query(domain, dns.rdatatype.A, dns.rdataclass.IN)
            # unset the Recurse flag 
            query.flags ^= dns.flags.RD
            try:
                # try the query
                response = dns.query.udp(query, nameserver)
                if len(response.answer) > 0:
                    self.alert('%s => Snooped!' % (domain))
                else:
                    self.verbose('%s => Not Found.' % (domain))
                continue
            except KeyboardInterrupt:
                print ''
                return
            except Exception as e:
                self.error(e.__str__())
                return