# -*- coding: utf-8 -*-
from collections import defaultdict
import mock
from searx.engines import twitter
from searx.testing import SearxTestCase


class TestTwitterEngine(SearxTestCase):

    def test_request(self):
        query = 'test_query'
        dicto = defaultdict(dict)
        dicto['pageno'] = 0
        dicto['language'] = 'fr_FR'
        params = twitter.request(query, dicto)
        self.assertIn('url', params)
        self.assertIn(query, params['url'])
        self.assertIn('twitter.com', params['url'])
        self.assertIn('cookies', params)
        self.assertIn('lang', params['cookies'])
        self.assertIn('fr', params['cookies']['lang'])

        dicto['language'] = 'all'
        params = twitter.request(query, dicto)
        self.assertIn('cookies', params)
        self.assertIn('lang', params['cookies'])
        self.assertIn('en', params['cookies']['lang'])

    def test_response(self):
        self.assertRaises(AttributeError, twitter.response, None)
        self.assertRaises(AttributeError, twitter.response, [])
        self.assertRaises(AttributeError, twitter.response, '')
        self.assertRaises(AttributeError, twitter.response, '[]')

        response = mock.Mock(text='<html></html>')
        self.assertEqual(twitter.response(response), [])

        html = """
        <li class="js-stream-item stream-item stream-item expanding-stream-item" data-item-id="563005573290287105"
            id="stream-item-tweet-563005573290287105" data-item-type="tweet">
            <div class="tweet original-tweet js-stream-tweet js-actionable-tweet js-profile-popup-actionable
                js-original-tweet has-cards has-native-media" data-tweet-id="563005573290287105" data-disclosure-type=""
                data-item-id="563005573290287105" data-screen-name="Jalopnik" data-name="Jalopnik"
                data-user-id="3060631" data-has-native-media="true" data-has-cards="true" data-card-type="photo"
                data-expanded-footer="&lt;div class=&quot;js-tweet-details-fixer
                tweet-details-fixer&quot;&gt;&#10;&#10;&#10;
                &lt;div class=&quot;cards-media-container js-media-container&quot;&gt;&lt;div
                data-card-url=&quot;//twitter.com/Jalopnik/status/563005573290287105/photo/1&quot; data-card-type=&quot;
                photo&quot; class=&quot;cards-base cards-multimedia&quot; data-element-context=&quot;platform_photo_card
                &quot;&gt;&#10;&#10;&#10;  &lt;a class=&quot;media media-thumbnail twitter-timeline-link is-preview
                &quot; data-url=&quot;https://pbs.twimg.com/media/B9Aylf5IMAAuziP.jpg:large&quot;
                data-resolved-url-large=&quot;https://pbs.twimg.com/media/B9Aylf5IMAAuziP.jpg:large&quot;
                href=&quot;//twitter.com/Jalopnik/status/563005573290287105/photo/1&quot;&gt;&#10;
                &lt;div class=&quot;&quot;&gt;&#10; &lt;img src=&quot;
                https://pbs.twimg.com/media/B9Aylf5IMAAuziP.jpg&quot;
                alt=&quot;Embedded image permalink&quot; width=&quot;636&quot; height=&quot;309&quot;&gt;&#10;
                &lt;/div&gt;&#10;&#10;  &lt;/a&gt;&#10;&#10;  &lt;div class=&quot;cards-content&quot;&gt;&#10;
                &lt;div class=&quot;byline&quot;&gt;&#10;      &#10;    &lt;/div&gt;&#10;    &#10;  &lt;/div&gt;&#10;
                &#10;&lt;/div&gt;&#10;&#10;&#10;&#10;&#10;&lt;/div&gt;&#10;&#10;&#10;&#10;  &lt;div
                class=&quot;js-machine-translated-tweet-container&quot;&gt;&lt;/div&gt;&#10;    &lt;div
                class=&quot;js-tweet-stats-container tweet-stats-container &quot;&gt;&#10;    &lt;/div&gt;&#10;&#10;
                &lt;div class=&quot;client-and-actions&quot;&gt;&#10;  &lt;span class=&quot;metadata&quot;&gt;&#10;
                &lt;span&gt;5:06 PM - 4 Feb 2015&lt;/span&gt;&#10;&#10;       &amp;middot; &lt;a
                class=&quot;permalink-link js-permalink js-nav&quot; href=&quot;/Jalopnik/status/563005573290287105
                &quot;tabindex=&quot;-1&quot;&gt;Details&lt;/a&gt;&#10;    &#10;&#10;        &#10;        &#10;
                &#10;&#10;  &lt;/span&gt;&#10;&lt;/div&gt;&#10;&#10;&#10;&lt;/div&gt;&#10;" data-you-follow="false"
                data-you-block="false">
                <div class="context">
                </div>
                <div class="content">
                    <div class="stream-item-header">
                        <a class="account-group js-account-group js-action-profile js-user-profile-link js-nav"
                            href="/Jalopnik" data-user-id="3060631">
                            <img class="avatar js-action-profile-avatar"
                                src="https://pbs.twimg.com/profile_images/2976430168/5cd4a59_bigger.jpeg" alt="">
                            <strong class="fullname js-action-profile-name show-popup-with-id" data-aria-label-part>
                                Jalopnik
                            </strong>
                            <span>&rlm;</span>
                            <span class="username js-action-profile-name" data-aria-label-part>
                            <s>@</s><b>TitleName</b>
                            </span>
                        </a>
                        <small class="time">
                        <a href="/this.is.the.url"
                            class="tweet-timestamp js-permalink js-nav js-tooltip" title="5:06 PM - 4 Feb 2015" >
                            <span class="u-hiddenVisually" data-aria-label-part="last">17 minutes ago</span>
                        </a>
                        </small>
                    </div>
                    <p class="js-tweet-text tweet-text" lang="en" data-aria-label-part="0">
                        This is the content étude à€
                        <a href="http://t.co/nRWsqQAwBL" rel="nofollow" dir="ltr"
                            data-expanded-url="http://jalo.ps/ReMENu4" class="twitter-timeline-link"
                            target="_blank" title="http://jalo.ps/ReMENu4" >
                        <span class="tco-ellipsis">
                        </span>
                        <span class="invisible">http://</span><span class="js-display-url">link.in.tweet</span>
                        <span class="invisible"></span>
                        <span class="tco-ellipsis">
                            <span class="invisible">&nbsp;</span>
                        </span>
                    </a>
                    <a href="http://t.co/rbFsfeE0l3" class="twitter-timeline-link u-hidden"
                        data-pre-embedded="true" dir="ltr">
                        pic.twitter.com/rbFsfeE0l3
                    </a>
                    </p>
                    <div class="expanded-content js-tweet-details-dropdown">
                    </div>
                    <div class="stream-item-footer">
                        <a class="details with-icn js-details" href="/Jalopnik/status/563005573290287105">
                            <span class="Icon Icon--photo">
                            </span>
                            <b>
                                <span class="expand-stream-item js-view-details">
                                    View photo
                                </span>
                                <span class="collapse-stream-item  js-hide-details">
                                    Hide photo
                                </span>
                            </b>
                        </a>
                        <span class="ProfileTweet-action--reply u-hiddenVisually">
                            <span class="ProfileTweet-actionCount" aria-hidden="true" data-tweet-stat-count="0">
                                <span class="ProfileTweet-actionCountForAria" >0 replies</span>
                            </span>
                        </span>
                        <span class="ProfileTweet-action--retweet u-hiddenVisually">
                            <span class="ProfileTweet-actionCount"  data-tweet-stat-count="8">
                                <span class="ProfileTweet-actionCountForAria" data-aria-label-part>8 retweets</span>
                            </span>
                        </span>
                        <span class="ProfileTweet-action--favorite u-hiddenVisually">
                            <span class="ProfileTweet-actionCount"  data-tweet-stat-count="14">
                                <span class="ProfileTweet-actionCountForAria" data-aria-label-part>14 favorites</span>
                            </span>
                        </span>
                        <div role="group" aria-label="Tweet actions" class="ProfileTweet-actionList u-cf js-actions">
                            <div class="ProfileTweet-action ProfileTweet-action--reply">
                                <button class="ProfileTweet-actionButton u-textUserColorHover js-actionButton
                                    js-actionReply" data-modal="ProfileTweet-reply" type="button" title="Reply">
                                    <span class="Icon Icon--reply">
                                    </span>
                                    <span class="u-hiddenVisually">Reply</span>
                                    <span class="ProfileTweet-actionCount u-textUserColorHover
                                        ProfileTweet-actionCount--isZero">
                                        <span class="ProfileTweet-actionCountForPresentation" aria-hidden="true">
                                        </span>
                                    </span>
                                </button>
                            </div>
                            <div class="ProfileTweet-action ProfileTweet-action--retweet js-toggleState js-toggleRt">
                                <button class="ProfileTweet-actionButton  js-actionButton js-actionRetweet js-tooltip"
                                    title="Retweet" data-modal="ProfileTweet-retweet" type="button">
                                    <span class="Icon Icon--retweet">
                                    </span>
                                    <span class="u-hiddenVisually">Retweet</span>
                                    <span class="ProfileTweet-actionCount">
                                        <span class="ProfileTweet-actionCountForPresentation">8</span>
                                    </span>
                                </button>
                                <button class="ProfileTweet-actionButtonUndo js-actionButton js-actionRetweet"
                                    data-modal="ProfileTweet-retweet" title="Undo retweet" type="button">
                                    <span class="Icon Icon--retweet">
                                    </span>
                                    <span class="u-hiddenVisually">Retweeted</span>
                                    <span class="ProfileTweet-actionCount">
                                        <span class="ProfileTweet-actionCountForPresentation">8</span>
                                    </span>
                                </button>
                            </div>
                            <div class="ProfileTweet-action ProfileTweet-action--favorite js-toggleState">
                                <button class="ProfileTweet-actionButton js-actionButton js-actionFavorite js-tooltip"
                                    title="Favorite" type="button">
                                    <span class="Icon Icon--favorite">
                                    </span>
                                    <span class="u-hiddenVisually">Favorite</span>
                                    <span class="ProfileTweet-actionCount">
                                        <span class="ProfileTweet-actionCountForPresentation">14</span>
                                    </span>
                                </button>
                                <button class="ProfileTweet-actionButtonUndo u-linkClean js-actionButton
                                    js-actionFavorite" title="Undo favorite" type="button">
                                    <span class="Icon Icon--favorite">
                                    </span>
                                    <span class="u-hiddenVisually">Favorited</span>
                                    <span class="ProfileTweet-actionCount">
                                        <span class="ProfileTweet-actionCountForPresentation">
                                            14
                                        </span>
                                    </span>
                                </button>
                            </div>
                            <div class="ProfileTweet-action ProfileTweet-action--more js-more-ProfileTweet-actions">
                                <div class="dropdown">
                                    <button class="ProfileTweet-actionButton u-textUserColorHover dropdown-toggle
                                        js-tooltip js-dropdown-toggle" type="button" title="More">
                                        <span class="Icon Icon--dots">
                                        </span>
                                        <span class="u-hiddenVisually">More</span>
                                    </button>
                                    <div class="dropdown-menu">
                                        <div class="dropdown-caret">
                                            <div class="caret-outer">
                                            </div>
                                            <div class="caret-inner">
                                            </div>
                                        </div>
                                        <ul>
                                            <li class="share-via-dm js-actionShareViaDM" data-nav="share_tweet_dm">
                                                <button type="button" class="dropdown-link">
                                                    Share via Direct Message
                                                </button>
                                            </li>
                                            <li class="embed-link js-actionEmbedTweet" data-nav="embed_tweet">
                                                <button type="button" class="dropdown-link">
                                                    Embed Tweet
                                                </button>
                                            </li>
                                            <li class="mute-user-item pretty-link">
                                                <button type="button" class="dropdown-link">
                                                    Mute
                                                </button>
                                            </li>
                                            <li class="unmute-user-item pretty-link">
                                                <button type="button" class="dropdown-link">
                                                    Unmute
                                                </button>
                                            </li>
                                            <li class="block-or-report-link js-actionBlockOrReport"
                                                data-nav="block_or_report">
                                                <button type="button" class="dropdown-link">
                                                    Block or report
                                                </button>
                                            </li>
                                        </ul>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </li>
        """
        response = mock.Mock(text=html)
        results = twitter.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], '@TitleName')
        self.assertEqual(results[0]['url'], 'https://twitter.com/this.is.the.url')
        self.assertIn(u'This is the content', results[0]['content'])
        # self.assertIn(u'This is the content étude à€', results[0]['content'])

        html = """
        <li class="js-stream-item stream-item stream-item expanding-stream-item" data-item-id="563005573290287105"
            id="stream-item-tweet-563005573290287105" data-item-type="tweet">
            <div class="tweet original-tweet js-stream-tweet js-actionable-tweet js-profile-popup-actionable
                js-original-tweet has-cards has-native-media" data-tweet-id="563005573290287105" data-disclosure-type=""
                data-item-id="563005573290287105" data-screen-name="Jalopnik" data-name="Jalopnik"
                data-user-id="3060631" data-has-native-media="true" data-has-cards="true" data-card-type="photo"
                data-expanded-footer="&lt;div class=&quot;js-tweet-details-fixer
                tweet-details-fixer&quot;&gt;&#10;&#10;&#10;
                &lt;div class=&quot;cards-media-container js-media-container&quot;&gt;&lt;div
                data-card-url=&quot;//twitter.com/Jalopnik/status/563005573290287105/photo/1&quot; data-card-type=&quot;
                photo&quot; class=&quot;cards-base cards-multimedia&quot; data-element-context=&quot;platform_photo_card
                &quot;&gt;&#10;&#10;&#10;  &lt;a class=&quot;media media-thumbnail twitter-timeline-link is-preview
                &quot; data-url=&quot;https://pbs.twimg.com/media/B9Aylf5IMAAuziP.jpg:large&quot;
                data-resolved-url-large=&quot;https://pbs.twimg.com/media/B9Aylf5IMAAuziP.jpg:large&quot;
                href=&quot;//twitter.com/Jalopnik/status/563005573290287105/photo/1&quot;&gt;&#10;
                &lt;div class=&quot;&quot;&gt;&#10; &lt;img src=&quot;
                https://pbs.twimg.com/media/B9Aylf5IMAAuziP.jpg&quot;
                alt=&quot;Embedded image permalink&quot; width=&quot;636&quot; height=&quot;309&quot;&gt;&#10;
                &lt;/div&gt;&#10;&#10;  &lt;/a&gt;&#10;&#10;  &lt;div class=&quot;cards-content&quot;&gt;&#10;
                &lt;div class=&quot;byline&quot;&gt;&#10;      &#10;    &lt;/div&gt;&#10;    &#10;  &lt;/div&gt;&#10;
                &#10;&lt;/div&gt;&#10;&#10;&#10;&#10;&#10;&lt;/div&gt;&#10;&#10;&#10;&#10;  &lt;div
                class=&quot;js-machine-translated-tweet-container&quot;&gt;&lt;/div&gt;&#10;    &lt;div
                class=&quot;js-tweet-stats-container tweet-stats-container &quot;&gt;&#10;    &lt;/div&gt;&#10;&#10;
                &lt;div class=&quot;client-and-actions&quot;&gt;&#10;  &lt;span class=&quot;metadata&quot;&gt;&#10;
                &lt;span&gt;5:06 PM - 4 Feb 2015&lt;/span&gt;&#10;&#10;       &amp;middot; &lt;a
                class=&quot;permalink-link js-permalink js-nav&quot; href=&quot;/Jalopnik/status/563005573290287105
                &quot;tabindex=&quot;-1&quot;&gt;Details&lt;/a&gt;&#10;    &#10;&#10;        &#10;        &#10;
                &#10;&#10;  &lt;/span&gt;&#10;&lt;/div&gt;&#10;&#10;&#10;&lt;/div&gt;&#10;" data-you-follow="false"
                data-you-block="false">
                <div class="context">
                </div>
                <div class="content">
                    <div class="stream-item-header">
                        <a class="account-group js-account-group js-action-profile js-user-profile-link js-nav"
                            href="/Jalopnik" data-user-id="3060631">
                            <img class="avatar js-action-profile-avatar"
                                src="https://pbs.twimg.com/profile_images/2976430168/5cd4a59_bigger.jpeg" alt="">
                            <strong class="fullname js-action-profile-name show-popup-with-id" data-aria-label-part>
                                Jalopnik
                            </strong>
                            <span>&rlm;</span>
                            <span class="username js-action-profile-name" data-aria-label-part>
                            <s>@</s><b>TitleName</b>
                            </span>
                        </a>
                        <small class="time">
                        <a href="/this.is.the.url"
                            class="tweet-timestamp js-permalink js-nav js-tooltip" title="5:06 PM - 4 Feb 2015" >
                            <span class="_timestamp js-short-timestamp js-relative-timestamp"  data-time="1423065963"
                                data-time-ms="1423065963000" data-long-form="true" aria-hidden="true">
                                17m
                            </span>
                            <span class="u-hiddenVisually" data-aria-label-part="last">17 minutes ago</span>
                        </a>
                        </small>
                    </div>
                    <p class="js-tweet-text tweet-text" lang="en" data-aria-label-part="0">
                        This is the content étude à€
                        <a href="http://t.co/nRWsqQAwBL" rel="nofollow" dir="ltr"
                            data-expanded-url="http://jalo.ps/ReMENu4" class="twitter-timeline-link"
                            target="_blank" title="http://jalo.ps/ReMENu4" >
                        <span class="tco-ellipsis">
                        </span>
                        <span class="invisible">http://</span><span class="js-display-url">link.in.tweet</span>
                        <span class="invisible"></span>
                        <span class="tco-ellipsis">
                            <span class="invisible">&nbsp;</span>
                        </span>
                    </a>
                    <a href="http://t.co/rbFsfeE0l3" class="twitter-timeline-link u-hidden"
                        data-pre-embedded="true" dir="ltr">
                        pic.twitter.com/rbFsfeE0l3
                    </a>
                    </p>
                    <div class="expanded-content js-tweet-details-dropdown">
                    </div>
                    <div class="stream-item-footer">
                        <a class="details with-icn js-details" href="/Jalopnik/status/563005573290287105">
                            <span class="Icon Icon--photo">
                            </span>
                            <b>
                                <span class="expand-stream-item js-view-details">
                                    View photo
                                </span>
                                <span class="collapse-stream-item  js-hide-details">
                                    Hide photo
                                </span>
                            </b>
                        </a>
                        <span class="ProfileTweet-action--reply u-hiddenVisually">
                            <span class="ProfileTweet-actionCount" aria-hidden="true" data-tweet-stat-count="0">
                                <span class="ProfileTweet-actionCountForAria" >0 replies</span>
                            </span>
                        </span>
                        <span class="ProfileTweet-action--retweet u-hiddenVisually">
                            <span class="ProfileTweet-actionCount"  data-tweet-stat-count="8">
                                <span class="ProfileTweet-actionCountForAria" data-aria-label-part>8 retweets</span>
                            </span>
                        </span>
                        <span class="ProfileTweet-action--favorite u-hiddenVisually">
                            <span class="ProfileTweet-actionCount"  data-tweet-stat-count="14">
                                <span class="ProfileTweet-actionCountForAria" data-aria-label-part>14 favorites</span>
                            </span>
                        </span>
                        <div role="group" aria-label="Tweet actions" class="ProfileTweet-actionList u-cf js-actions">
                            <div class="ProfileTweet-action ProfileTweet-action--reply">
                                <button class="ProfileTweet-actionButton u-textUserColorHover js-actionButton
                                    js-actionReply" data-modal="ProfileTweet-reply" type="button" title="Reply">
                                    <span class="Icon Icon--reply">
                                    </span>
                                    <span class="u-hiddenVisually">Reply</span>
                                    <span class="ProfileTweet-actionCount u-textUserColorHover
                                        ProfileTweet-actionCount--isZero">
                                        <span class="ProfileTweet-actionCountForPresentation" aria-hidden="true">
                                        </span>
                                    </span>
                                </button>
                            </div>
                            <div class="ProfileTweet-action ProfileTweet-action--retweet js-toggleState js-toggleRt">
                                <button class="ProfileTweet-actionButton  js-actionButton js-actionRetweet js-tooltip"
                                    title="Retweet" data-modal="ProfileTweet-retweet" type="button">
                                    <span class="Icon Icon--retweet">
                                    </span>
                                    <span class="u-hiddenVisually">Retweet</span>
                                    <span class="ProfileTweet-actionCount">
                                        <span class="ProfileTweet-actionCountForPresentation">8</span>
                                    </span>
                                </button>
                                <button class="ProfileTweet-actionButtonUndo js-actionButton js-actionRetweet"
                                    data-modal="ProfileTweet-retweet" title="Undo retweet" type="button">
                                    <span class="Icon Icon--retweet">
                                    </span>
                                    <span class="u-hiddenVisually">Retweeted</span>
                                    <span class="ProfileTweet-actionCount">
                                        <span class="ProfileTweet-actionCountForPresentation">8</span>
                                    </span>
                                </button>
                            </div>
                            <div class="ProfileTweet-action ProfileTweet-action--favorite js-toggleState">
                                <button class="ProfileTweet-actionButton js-actionButton js-actionFavorite js-tooltip"
                                    title="Favorite" type="button">
                                    <span class="Icon Icon--favorite">
                                    </span>
                                    <span class="u-hiddenVisually">Favorite</span>
                                    <span class="ProfileTweet-actionCount">
                                        <span class="ProfileTweet-actionCountForPresentation">14</span>
                                    </span>
                                </button>
                                <button class="ProfileTweet-actionButtonUndo u-linkClean js-actionButton
                                    js-actionFavorite" title="Undo favorite" type="button">
                                    <span class="Icon Icon--favorite">
                                    </span>
                                    <span class="u-hiddenVisually">Favorited</span>
                                    <span class="ProfileTweet-actionCount">
                                        <span class="ProfileTweet-actionCountForPresentation">
                                            14
                                        </span>
                                    </span>
                                </button>
                            </div>
                            <div class="ProfileTweet-action ProfileTweet-action--more js-more-ProfileTweet-actions">
                                <div class="dropdown">
                                    <button class="ProfileTweet-actionButton u-textUserColorHover dropdown-toggle
                                        js-tooltip js-dropdown-toggle" type="button" title="More">
                                        <span class="Icon Icon--dots">
                                        </span>
                                        <span class="u-hiddenVisually">More</span>
                                    </button>
                                    <div class="dropdown-menu">
                                        <div class="dropdown-caret">
                                            <div class="caret-outer">
                                            </div>
                                            <div class="caret-inner">
                                            </div>
                                        </div>
                                        <ul>
                                            <li class="share-via-dm js-actionShareViaDM" data-nav="share_tweet_dm">
                                                <button type="button" class="dropdown-link">
                                                    Share via Direct Message
                                                </button>
                                            </li>
                                            <li class="embed-link js-actionEmbedTweet" data-nav="embed_tweet">
                                                <button type="button" class="dropdown-link">
                                                    Embed Tweet
                                                </button>
                                            </li>
                                            <li class="mute-user-item pretty-link">
                                                <button type="button" class="dropdown-link">
                                                    Mute
                                                </button>
                                            </li>
                                            <li class="unmute-user-item pretty-link">
                                                <button type="button" class="dropdown-link">
                                                    Unmute
                                                </button>
                                            </li>
                                            <li class="block-or-report-link js-actionBlockOrReport"
                                                data-nav="block_or_report">
                                                <button type="button" class="dropdown-link">
                                                    Block or report
                                                </button>
                                            </li>
                                        </ul>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </li>
        """
        response = mock.Mock(text=html)
        results = twitter.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], '@TitleName')
        self.assertEqual(results[0]['url'], 'https://twitter.com/this.is.the.url')
        self.assertIn(u'This is the content', results[0]['content'])

        html = """
        <li class="b_algo" u="0|5109|4755453613245655|UAGjXgIrPH5yh-o5oNHRx_3Zta87f_QO">
            <div Class="sa_mc">
                <div class="sb_tlst">
                    <h2>
                        <a href="http://this.should.be.the.link/" h="ID=SERP,5124.1">
                        <strong>This</strong> should be the title</a>
                    </h2>
                </div>
                <div class="sb_meta">
                <cite>
                <strong>this</strong>.meta.com</cite>
                    <span class="c_tlbxTrg">
                        <span class="c_tlbxH" H="BASE:CACHEDPAGEDEFAULT" K="SERP,5125.1">
                        </span>
                    </span>
                </div>
                <p>
                <strong>This</strong> should be the content.</p>
            </div>
        </li>
        """
        response = mock.Mock(text=html)
        results = twitter.response(response)
        self.assertEqual(type(results), list)
        self.assertEqual(len(results), 0)
