# -*- coding: utf-8 -*-

from collections import defaultdict
import mock
from searx.engines import google_news
from searx.testing import SearxTestCase


class TestGoogleNewsEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 1
        dicto['language'] = 'fr_FR'
        dicto['time_range'] = 'w'
        params = google_news.request(query, dicto)
        self.assertIn('url', params)
        self.assertIn(query, params['url'])
        self.assertIn('fr', params['url'])

        dicto['language'] = 'all'
        params = google_news.request(query, dicto)
        self.assertIn('url', params)
        self.assertNotIn('fr', params['url'])

    def test_response(self):
        self.assertRaises(AttributeError, google_news.response, None)
        self.assertRaises(AttributeError, google_news.response, [])
        self.assertRaises(AttributeError, google_news.response, '')
        self.assertRaises(AttributeError, google_news.response, '[]')

        response = mock.Mock(text='{}')
        self.assertEqual(google_news.response(response), [])

        response = mock.Mock(text='{"data": []}')
        self.assertEqual(google_news.response(response), [])

        html = u"""
<div class="g">
<div class="ts _V6c _Zmc _XO _knc _d7c"><a class="top _vQb _mnc" href="http://this.is.the.url" onmousedown="return rwt(this,'','','','5','AFQjCNGixEtJGC3qTB9pYFLXlRj8XXwdiA','','0ahUKEwiG7O_M5-rQAhWDtRoKHd0RD5QQvIgBCCwwBA','','',event)"><img class="th _lub" id="news-thumbnail-image-52779299683347" src="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAkGBwgHBgkIBwgKCgkLDRYPDQwMDRsUFRAWIB0iIiAdHx8kKDQsJCYxJx8fLT0tMTU3Ojo6Iys/RD84QzQ5OjcBCgoKDQwNGg8PGjclHyU3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3N//AABEIAGQAZAMBIgACEQEDEQH/xAAbAAACAwEBAQAAAAAAAAAAAAAFBgADBAIBB//EADsQAAIBAwIEAwUGBAUFAAAAAAECAwAEEQUhBhIxURNBYRQiMnGBFSORobHBB1Ji4UKS0fDxFiQzNYL/xAAYAQEBAQEBAAAAAAAAAAAAAAACAwEEAP/EACERAAMBAAICAgMBAAAAAAAAAAABAhEhMQMSE2EEQVEi/9oADAMBAAIRAxEAPwDSkKr8JFWIzwnMTlSepFdiBgMiuxEdid6B7QbrEr8qE4L4wGNCIT7u/WifE0eIosHBz0oWnugCjQ4BfEipJHbpK/JG0gDP/KO9XT6Lw7BGDHrofIBIJQ4NXalAs8IDJnFLepS21pmOOFXl679FoY66ZTcNwWxtGzaaqwOf8JFcXupSSr4cupSOp6gnGaDQahJESQwU/wBIxXbX0l0jl+VgduYjJrfj/ofc9MluueV1z3xV2jlX1AlDkY61TY3MAk5LuJSnm4G4+nnTFb2ltEweFRvuCO1ebw8uTYNnQ9iDTtDKJYY8DflFJgXLp8xT5FbJHBGx/lFFM9a4MrQFjnFSilvPGiYaItv1zUrTnwHljgLViqwUDyNFEskKlmIDCs08JMWHfl32INZ8hnIscWII4oWPmdqCg9KLccsUtLZM596g6HmVT6Um9WlvGeXk/gWruCObGFz3pb0/R59Y1D2WDYk5lmfpGP3PpW7iK4aIxY3CqWA7t5UxcG3SQWxsZI2VI0MxM6hedj1Oeo9Kc5M6PPagQ3DdjpcpWeHx2U7s+9LuvPCsr+yoETIwAOgpq1DV59RmuJIpbS2hhOG5zvmlLVXE4OCpcnBKdDRW7ptZgMEuCCPrTJwteGYS2z78vvpnt5j/AH3pWIxRbhZ+XV4h5Orj8s/tTtcE5fI6xKWmjVepYfrX0trQrbxLICDyDavm0EvgXEU2M8jhsfI033fHiyxxSfZkwj+EtjP6VzpPR0E8ICQR0qUuT8Y2DSExxtj69alVwOINy3Esye7zKfnXdpZzzMjSfAO1KGm8UX99qNvbm1SNZZApYnoPOimr6rf2crBLmQoTsFIwo8htUHDRk+N0Zv4nQi2itMHALUAiP3SH0oxJrUtyqJcKk4GDiZeb9a0LqkOADY2nz8FaSeLCkxgsWUVrecWQRXwDQW8DzMpGckdNvPr0orxZfpa2if8AYywPIfDkY4YDYHbHbcVgucf9YWd3CqR+MxUgDC5C7bDy2FecRzXQsxJd3lmJN8wCPCvgkZBBOc1Vr2kccaA7PkuBOm6qzD3+XZh1/UflWG+isoGAgMjPzb8x2Jz2r37Sm8AouynqKFyOQxkk8unqa9KYKawolI529CRRLhr/ANxb46AOT/lNBgSTTPwTL7PqMlwpHOkXKuR3IzTvonPY2WqCa6hiPR3VT9TTfx3pzaRb2IskUJICpBPUgUvDXphjLR5HQ8oq6bii9uOUXExmC/CJBzY/GoTWFXOiKV1BZpvEjJYyEkgbb1Kdvt19j9zk9fuk/wBKlL5foz0Zk0vTWa0N/hyVYqiKcZ26/jSvdX81pqET+0PJCX8Nw3l6H5b19H0pccPWpxu2WO/9R3pQ4s0yzi1K4gcFGuW8WN+b3STny8t6xr9lU+MRe2AQVPukZGKq9qTxzCGJcLzbHIqm2uILSCO2uiyvF7pdh1HUNjtQO0uootbLSmQ25kIfwyOYrnyztmvT/oL4C91M3NHIh96GRZB9D+/T61xxNf6XqbBrC2LSbkhVyfypk1Cew1SP7F0exNjbW8LXeovKwMx5VJCs3/0vToT6EUhcHTqOIEfConIyLy+QNX9MWElYOmkYHDKVx5EYrFIrSNk7imriCFrm7kt+TM8R5ie696y6Do41G5naUlLa2TnkxjJ7L9TR3BOdeCzgbg82fntRvR1mtbpGYe5IvUdiP7isrWDSTuIwFIyewA+tbraC7js4J7WVpYz92VUZMTdeUr28wenX1rXyg+rTC7TkHrXonPeiGk6TFeWeNQuWsLot7kkihoXHrj3l+e4oZJbSxzTxY5mgcrJyHmAx57eXrXOVc1Pawt8dq8rPv5VKww+jWUgbhGymTO8QIPod6y8cadHfaQsgws8GWUjrjO4/erXxa8M2cETZCW6bEdNq513UlsbSO6mh9oRXXmh5+UPkk4Jx54NdUrQ08Qj2cQ1ezMDkpexA7k/EBQ+C3ubOVXliICts3l1rXqEr3+qPeWASK7n55vZ7bHhxDGeQf1coJP4dc13Y8SMiPDeRBiRjp19DUaiofBs3NLkKahcwcNaLJaQMtzquspz3jhuYRRE5EYPc9W/4oDDYGyvLO4upLdB4YzFFJmRQq5HMvcj9qtvI7SPXpGguxqFvFysZSvKHON167gdM1a/EUb6fLYz2FvI01yJZrphmVlyCVHYfLue9dTWyRisotfVpLm8D272suB0mURtjtkV3p2qwWF5P7VbmETAK6ZyrD0odrtq+nTiy1PT47Oc4mWWPBflYbA4OMenWsdnd3FusqxOkyMpVkYdR9a5nLXBer2tQyxRWcjznT5CpfDBMbtjoPl6VlN+sCLNbwMZjIysoAGPQj8OtBre5dJeaPKN5ods0aGoW2o2rQ3i/eHYSpsw+dTc4dng/L9J9WjSsK3Og3V/JeQWvhL4cUcr5Zj5j0JGw9aG6Jpst3NDFLcmzNzA8ts2ATIyZ265Xz/vtWbVbOzgQCW4eJ4oT4I8MkSHyUYHmepJAHY0PWGSbT11CFFSGKQwM6EhmYjOTv2OM7darCyeDl/J8r8nk1sIwXDSRK7jDHrnY586lNuh6Pouu6Xb3ZvE06ZV8KaFCFUuvVgD0zsa8oNE9CmpA/YtoRkhrdPptWPidZ5dGuIraETSye6V64jQB3IH82QD8gcb1gvuIDJp9vaW8JVkRYyZN8kDyArBbXx1XXLO2vb2SKI8yyGBSFRSu+MZJzhc/6V1QsYLeo1R3Oh3dnby6RYvDcWcQE1wUVRM3KASQCd/n39aUkhN7rltFJ1muI0OP6mA/ejeqX1jYaxLpOmzmfT4IQgmOMu5PMzbAdwPpS+l37Pq8NzGvM0Myui9yrAgfpXrfIZ6CkmjXWpa9qcPD9s3hQvIyoGGBGrcvmfP96OcI8YaTpelw2mp6MJkR2cThVkEj9dww28umdsVm0HSotb1O6tbK5v8ATp1R2dmcOo94Aqccp8/yoHxBbrpt39lLMswtCweRVwGdt2/ABR9KbWAX2aNX1231DiCXVru3M5kkLmGR/cIxhV+QAH4UHvbqC5lMsFvFa7Y5Yc4P4k0X1vS7XS9E0znwb+6BmkXkX3E8t8ZzuOpxsawXEa6Td3MKrHLJ4JhdiPgYgc2PUbrn51Nz/WPfoxpOcY8QEjbB3q2KUswzjbzWt+t3Ftcw2Hh28cKwRLCzqP8AydMtjA32rnUtG9jiS4srhJ7OT4JUYZ+TDqDQpCVFpmW/g9llYArvGxHwmrNX0v2HQdKkjcxx3HOZk5jhnGMk9+woRFKUO/Uedbprye8tGiZs28Eikcx+FmBG3ocfkKKWcG1zyPv8PLi2Xh3wpbOSQxTuodFHvA4PbuTUpG07XtW0qA29lMYoy3MVx5kD07AVKxzyZphmvZnWViR/KMeQrvQ4lutQm8bJ8G0lmUZ/xKuRn61KldDACoHYzu7MSx6sepo9pFtE/vMMloyT9cj8sV7UoPsS6G7+HX3Wm6jdLvM0ioWPYLn9SaQFka91NHuTzme4Bkz58zb/AK17Uq1dImg5rcrXPGcUU2GSIxqq+QGA36ml+bMkaXEjM0kw8R89yd6lSpiCfCcEV7fXdpcxq8TWUjjujAggr2NXcJ3k08F9pcpDWslpJNyEfA6gEFe29SpQZqAgbmAY9TvXAY5YZOCRUqV79ifRthucRhXgglxsGkTmIHbNSpUrAn//2Q==" alt="A(z) south témájának képe a következőből: CBC.ca" data-deferred="1" onload="google.aft&amp;&amp;google.aft(this)"></a><div class="_cnc"><h3 class="r _U6c"><a class="l _HId" href="http://this.is.the.url" onmousedown="return rwt(this,'','','','5','AFQjCNGixEtJGC3qTB9pYFLXlRj8XXwdiA','','0ahUKEwiG7O_M5-rQAhWDtRoKHd0RD5QQqQIILSgAMAQ','','',event)">Meet Thuli Madonsela — <em>South</em> Africa's conscience</a></h3><div class="slp"><span class="_tQb _IId">CBC.ca</span><span class="_v5">-</span><span class="f nsa _uQb">9 órával ezelőtt</span></div><div class="st"><em>South</em> African Public Protector</div></div><div class="_Xmc card-section"><a class="_sQb" href="http://www.news24.com/Columnists/Mpumelelo_Mkhabela/who-really-governs-south-africa-20161209" onmousedown="return rwt(this,'','','','5','AFQjCNHhc2MnYSZ5T4COqInzvgoju5k5bA','','0ahUKEwiG7O_M5-rQAhWDtRoKHd0RD5QQuogBCC4oATAE','','',event)">Who really governs <em>South</em> Africa?</a><br><span class="_Wmc _GId">Vélemény</span><span class="_v5">-</span><span class="_tQb _IId">News24</span><span class="_v5">-</span><span class="f nsa _uQb">2016. dec. 8.</span></div><div class="_Vmc"></div></div>
</div>
        """  # noqa
        response = mock.Mock(text=html)
        results = google_news.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], u'Meet Thuli Madonsela \u2014 South Africa\'s conscience')
        self.assertEqual(results[0]['url'], 'http://this.is.the.url')
        self.assertEqual(results[0]['content'], 'South African Public Protector')
