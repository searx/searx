from searx.url_utils import urlencode

try:
    from HTMLParser import HTMLParser
except:
    from html.parser import HTMLParser

url = 'http://www.filecrop.com/'
search_url = url + '/search.php?{query}&size_i=0&size_f=100000000&engine_r=1&engine_d=1&engine_e=1&engine_4=1&engine_m=1&pos={index}'  # noqa

paging = True


class FilecropResultParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.__start_processing = False

        self.results = []
        self.result = {}

        self.tr_counter = 0
        self.data_counter = 0

    def handle_starttag(self, tag, attrs):

        if tag == 'tr':
            if ('bgcolor', '#edeff5') in attrs or\
               ('bgcolor', '#ffffff') in attrs:
                self.__start_processing = True

        if not self.__start_processing:
            return

        if tag == 'label':
            self.result['title'] = [attr[1] for attr in attrs
                                    if attr[0] == 'title'][0]
        elif tag == 'a' and ('rel', 'nofollow') in attrs\
                and ('class', 'sourcelink') in attrs:
            if 'content' in self.result:
                self.result['content'] += [attr[1] for attr in attrs
                                           if attr[0] == 'title'][0]
            else:
                self.result['content'] = [attr[1] for attr in attrs
                                          if attr[0] == 'title'][0]
            self.result['content'] += ' '
        elif tag == 'a':
            self.result['url'] = url + [attr[1] for attr in attrs
                                        if attr[0] == 'href'][0]

    def handle_endtag(self, tag):
        if self.__start_processing is False:
            return

        if tag == 'tr':
            self.tr_counter += 1

            if self.tr_counter == 2:
                self.__start_processing = False
                self.tr_counter = 0
                self.data_counter = 0
                self.results.append(self.result)
                self.result = {}

    def handle_data(self, data):
        if not self.__start_processing:
            return

        if 'content' in self.result:
            self.result['content'] += data + ' '
        else:
            self.result['content'] = data + ' '

        self.data_counter += 1


def request(query, params):
    index = 1 + (params['pageno'] - 1) * 30
    params['url'] = search_url.format(query=urlencode({'w': query}), index=index)
    return params


def response(resp):
    parser = FilecropResultParser()
    parser.feed(resp.text)

    return parser.results
