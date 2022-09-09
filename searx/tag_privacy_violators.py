import socket
import ipwhois
from searx import logger

ASN_PRIVACY = {
    # Akamai
    "55770": "Akamai",
    "55409": "Akamai",
    "49846": "Akamai",
    "49249": "Akamai",
    "48163": "Akamai",
    "45700": "Akamai",
    "43639": "Akamai",
    "39836": "Akamai",
    "393560": "Akamai",
    "393234": "Akamai",
    "36183": "Akamai",
    "36029": "Akamai",
    "35994": "Akamai",
    "35993": "Akamai",
    "35204": "Akamai",
    "34850": "Akamai",
    "34164": "Akamai",
    "33905": "Akamai",
    "32787": "Akamai",
    "31377": "Akamai",
    "31110": "Akamai",
    "31109": "Akamai",
    "31108": "Akamai",
    "31107": "Akamai",
    "30675": "Akamai",
    "26008": "Akamai",
    "24319": "Akamai",
    "23903": "Akamai",
    "23455": "Akamai",
    "23454": "Akamai",
    "22452": "Akamai",
    "22207": "Akamai",
    "21399": "Akamai",
    "21357": "Akamai",
    "21342": "Akamai",
    "20940": "Akamai",
    "20189": "Akamai",
    "18717": "Akamai",
    "18680": "Akamai",
    "17334": "Akamai",
    "16702": "Akamai",
    "16625": "Akamai",
    "12222": "Akamai",
    # Alibaba
    "45104": "Alibaba",
    "45103": "Alibaba",
    "45102": "Alibaba",
    "45096": "Alibaba",
    "37963": "Alibaba",
    "34947": "Alibaba",
    "134963": "Alibaba",
    # Amazon
    "9059": "Amazon",
    "8987": "Amazon",
    "7224": "Amazon",
    "62785": "Amazon",
    "58588": "Amazon",
    "395343": "Amazon",
    "39111": "Amazon",
    "38895": "Amazon",
    "264167": "Amazon",
    "19047": "Amazon",
    "17493": "Amazon",
    "16509": "Amazon",
    "14618": "Amazon",
    "135630": "Amazon",
    "10124": "Amazon",
    # Aryaka Networks, Inc
    "11179": "Aryaka Networks",
    # Azure
    "53587": "Azure",
    "24221": "Azure",
    "134235": "Azure",
    # Cloudflare
    "395747": "Cloudflare",
    "394536": "Cloudflare",
    "209242": "Cloudflare",
    "203898": "Cloudflare",
    "202623": "Cloudflare",
    "14789": "Cloudflare",
    "139242": "Cloudflare",
    "133877": "Cloudflare",
    "13335": "Cloudflare",
    # CDNetworks Inc
    "43303": "CDNetworks",
    "40366": "CDNetworks",
    "38670": "CDNetworks",
    "38107": "CDNetworks",
    "36408": "CDNetworks",
    "204720": "CDNetworks",
    # EdgeCast Networks, Inc. d/b/a Verizon Digital Media Services
    "15133": "EdgeCast Networks",
    # Highwinds Network Group, Inc.
    "33438": "Highwinds Network",
    "29798": "Highwinds Network",
    "20446": "Highwinds Network",
    "18607": "Highwinds Network",
    "11588": "Highwinds Network",
    # Incapsula Inc
    "19551": "Incapsula",
    # Instart Logic, Inc
    "33047": "Instant Logics",
    "133103": "Instant Logics",
    "6993": "Instant Logics",
    "55755": "Instant Logics",
    "48910": "Instant Logics",
    "4513": "Instant Logics",
    "30637": "Instant Logics",
    "30636": "Instant Logics",
    "30282": "Instant Logics",
    "29791": "Instant Logics",
    "24295": "Instant Logics",
    "24247": "Instant Logics",
    "24246": "Instant Logics",
    "24245": "Instant Logics",
    "22212": "Instant Logics",
    "22211": "Instant Logics",
    "22132": "Instant Logics",
    "19024": "Instant Logics",
    "17675": "Instant Logics",
    "15570": "Instant Logics",
    "15421": "Instant Logics",
    "14745": "Instant Logics",
    "14744": "Instant Logics",
    "14743": "Instant Logics",
    "14742": "Instant Logics",
    "14636": "Instant Logics",
    "13890": "Instant Logics",
    "13792": "Instant Logics",
    "13791": "Instant Logics",
    "13790": "Instant Logics",
    "13789": "Instant Logics",
    "12182": "Instant Logics",
    "12181": "Instant Logics",
    "12180": "Instant Logics",
    "12179": "Instant Logics",
    "12178": "Instant Logics",
    "11855": "Instant Logics",
    "11854": "Instant Logics",
    "11853": "Instant Logics",
    "10913": "Instant Logics",
    "10912": "Instant Logics",
    "10911": "Instant Logics",
    "10910": "Instant Logics",
    # Fastly
    "54113": "Fastly",
    "394192": "Fastly",
    # Google
    "45566": "Google",
    "43515": "Google",
    "41264": "Google",
    "40873": "Google",
    "396982": "Google",
    "395973": "Google",
    "394699": "Google",
    "394639": "Google",
    "394507": "Google",
    "36987": "Google",
    "36492": "Google",
    "36385": "Google",
    "36384": "Google",
    "36040": "Google",
    "36039": "Google",
    "26910": "Google",
    "26684": "Google",
    "22859": "Google",
    "22577": "Google",
    "19527": "Google",
    "16550": "Google",
    "15169": "Google",
    "13949": "Google",
    "139190": "Google",
    "139070": "Google",
    # Limelight
    "60261": "Limelight",
    "55429": "Limelight",
    "45396": "Limelight",
    "38622": "Limelight",
    "38621": "Limelight",
    "37277": "Limelight",
    "27191": "Limelight",
    "26506": "Limelight",
    "25804": "Limelight",
    "23164": "Limelight",
    "23135": "Limelight",
    "23059": "Limelight",
    "22822": "Limelight",
    "12411": "Limelight",
    # Yottaa, Inc
    "393259": "Yottaa",
}


class TagPrivacyViolators:
    """ Tags websites that violate user's privacy. """

    def __init__(self):
        self.cache = {}
    def find_privacy_violators(self,results):
        """ Finds websites that violate privacy through querying whois and looking up their asn value. """
        tagged_websites = {}
        for result in results:
            logger.debug('cache: %s', ', '.join(self.cache))
            if result['parsed_url'].netloc in self.cache:
                logger.info("%s is in cache",result['url'])
                tagged_websites[result['url']] = self.cache.get(result['parsed_url'].netloc)
                continue
            try:
                ipwhois_obj = ipwhois.IPWhois(
                    socket.gethostbyname(
                        result['parsed_url'].netloc
                    ) ,timeout=2
                )
                answer = ipwhois_obj.lookup_rdap()
                asn_value = ASN_PRIVACY.get(answer['asn'])
            except Exception as e:
                logger.error(e)
            if asn_value:
                tagged_websites[result['url']] = asn_value
                self.cache[result['parsed_url'].netloc] = asn_value
        return tagged_websites
