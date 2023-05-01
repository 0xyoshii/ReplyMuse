import requests
import re 
from askmuse import AskMuse
import time
import logging
from dotenv import load_dotenv
load_dotenv()
import os

BEARER = os.environ.get("BEARER")
CSRF = os.environ.get("CSRF")
AUTH_TOKEN = os.environ.get("AUTH_TOKEN")

logging.basicConfig(
    filename = 'file.log',
    level = logging.DEBUG,
    format = '%(asctime)s:%(levelname)s:%(name)s:%(message)s'
)

class TwitterClient:
    def __init__(self):
        self.since_id = ""
        self.headers = {
            'sec-ch-ua': '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
            'x-twitter-client-language': 'en',
            'x-csrf-token': CSRF,
            'sec-ch-ua-mobile': '?0',
            'authorization': f'Bearer {BEARER}',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
            'content-type': 'application/json',
            'cookie': f'auth_token={AUTH_TOKEN}; ct0={CSRF};',
            'referer': 'https://twitter.com/home',
            'x-twitter-auth-type': 'OAuth2Session',
            'x-twitter-active-user': 'yes',
            'sec-ch-ua-platform': '"macOS"'
        }
        self.createUri = "https://twitter.com/i/api/graphql/1RyAhNwby-gzGCRVsMxKbQ/CreateTweet"
        self.mentionsUri = "https://api.twitter.com/1.1/statuses/mentions_timeline.json?count=10&since_id="
        self.delay = 5

        pass


    def checkMentions(self):
        r = requests.get('https://api.twitter.com/1.1/statuses/mentions_timeline.json?count=10', headers=self.headers)
        data = r.json()
        if len(data) > 0:
            self.since_id = data[0]["id_str"]
        else:
            self.since_id = "1650953166135914526"

        while True:
            try:
                #print(self.since_id)
                r = requests.get(self.mentionsUri + self.since_id, headers=self.headers)
                data = r.json()
            

                if len(data) > 0:
                    try:
                        logging.info(" Found mentions - " + str(len(data)))
                        data.reverse()
                    except:
                        logging.info(" Found mention")
                        pass
                    for value in data:
                        self.since_id = value["id_str"]
                        if value["text"].replace(" ", "") == "@ReplyMuse":
                            s = requests.get(f'https://twitter.com/i/api/graphql/BbCrSoXIR7z93lLCVFlQ2Q/TweetDetail?variables=%7B%22focalTweetId%22%3A%22{value["in_reply_to_status_id_str"]}%22%2C%22referrer%22%3A%22tweet%22%2C%22with_rux_injections%22%3Afalse%2C%22includePromotedContent%22%3Atrue%2C%22withCommunity%22%3Atrue%2C%22withQuickPromoteEligibilityTweetFields%22%3Atrue%2C%22withBirdwatchNotes%22%3Atrue%2C%22withVoice%22%3Atrue%2C%22withV2Timeline%22%3Atrue%7D&features=%7B%22blue_business_profile_image_shape_enabled%22%3Atrue%2C%22responsive_web_graphql_exclude_directive_enabled%22%3Atrue%2C%22verified_phone_label_enabled%22%3Afalse%2C%22responsive_web_graphql_timeline_navigation_enabled%22%3Atrue%2C%22responsive_web_graphql_skip_user_profile_image_extensions_enabled%22%3Afalse%2C%22tweetypie_unmention_optimization_enabled%22%3Atrue%2C%22vibe_api_enabled%22%3Atrue%2C%22responsive_web_edit_tweet_api_enabled%22%3Atrue%2C%22graphql_is_translatable_rweb_tweet_is_translatable_enabled%22%3Atrue%2C%22view_counts_everywhere_api_enabled%22%3Atrue%2C%22longform_notetweets_consumption_enabled%22%3Atrue%2C%22tweet_awards_web_tipping_enabled%22%3Afalse%2C%22freedom_of_speech_not_reach_fetch_enabled%22%3Afalse%2C%22standardized_nudges_misinfo%22%3Atrue%2C%22tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled%22%3Afalse%2C%22interactive_text_enabled%22%3Atrue%2C%22responsive_web_text_conversations_enabled%22%3Afalse%2C%22longform_notetweets_rich_text_read_enabled%22%3Atrue%2C%22responsive_web_enhance_cards_enabled%22%3Afalse%7D', headers=self.headers)
                            data = s.json()["data"]["threaded_conversation_with_injections_v2"]["instructions"][0]["entries"][len(s.json()["data"]["threaded_conversation_with_injections_v2"]["instructions"][0]["entries"]) - 2]["content"]["itemContent"]["tweet_results"]["result"]["legacy"]["full_text"]
                            self.tweet(" ".join([word for word in data.split() if not word.startswith('@')]), value["id_str"])
                        else:
                            self.tweet(re.sub(r'@\w+\s?', '', value["text"]), value["id_str"])
                else:
                    logging.debug(" No new mentions found, retrying")
                    time.sleep(self.delay)

            except Exception as e:
                logging.error("Error checking mentions - ", e)
                return

        

    def tweet(self, text, tId):
        while True:
            try:
                museClient = AskMuse(" ".join(re.sub(r'[^%\w]', ' ', text).split()))
                statsData = museClient.ask()
                data = {"variables":{"tweet_text":statsData,"reply":{"in_reply_to_tweet_id":tId,"exclude_reply_user_ids":[]},"dark_request":False,"media":{"media_entities":[],"possibly_sensitive":False},"semantic_annotation_ids":[]},"features":{"tweetypie_unmention_optimization_enabled":True,"vibe_api_enabled":True,"responsive_web_edit_tweet_api_enabled":True,"graphql_is_translatable_rweb_tweet_is_translatable_enabled":True,"view_counts_everywhere_api_enabled":True,"longform_notetweets_consumption_enabled":True,"tweet_awards_web_tipping_enabled":False,"interactive_text_enabled":True,"responsive_web_text_conversations_enabled":False,"longform_notetweets_rich_text_read_enabled":True,"blue_business_profile_image_shape_enabled":True,"responsive_web_graphql_exclude_directive_enabled":True,"verified_phone_label_enabled":False,"freedom_of_speech_not_reach_fetch_enabled":False,"standardized_nudges_misinfo":True,"tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled":False,"responsive_web_graphql_skip_user_profile_image_extensions_enabled":False,"responsive_web_graphql_timeline_navigation_enabled":True,"responsive_web_enhance_cards_enabled":False},"queryId":"1RyAhNwby-gzGCRVsMxKbQ"}
                r = requests.post(
                    self.createUri, 
                    headers=self.headers,
                    json=data
                    )
                if r.status_code == 200:
                    logging.info("Successfully tweeted response")
                    return
                else:
                    logging.error("Error sending tweet - ", r.status_code)
                    return
            except Exception as e:
                logging.error("Error tweeting - ", str(e))
                return

if __name__ == '__main__':
    client = TwitterClient()
    client.checkMentions()

