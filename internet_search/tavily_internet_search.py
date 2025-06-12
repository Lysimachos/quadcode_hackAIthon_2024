from tavily import TavilyClient
import json


class TavilyInternetSearch:
    def __init__(self, tavily_api_key):
        self.client = TavilyClient(api_key=tavily_api_key)
        from openai import OpenAI
        self.openai_client = OpenAI()

    def _get_system_context(self):
        return {
                "role": "system",
                "content": f'You are an AI critical thinker research assistant. ' \
                           f'Your sole purpose is to write clean, very lean, critically acclaimed,' \
                           f'objective, reliable and well-structured report on a given text.' \
                           f'You should totally neglect text from websites that are'
                           f' missing https certificate or websites that are not in English.'
            }
    def _get_user_context(self, agent_query, content):
        return {
                "role": "user",
                "content":  f'Using information below, collected from the web, answer the following query.'
                            f'Your output should be strictly a list of dictionaries with fields: report, url, tittle, score, source \n\n' \
                           
                            f'query: "{agent_query}" \n\n' \
                            f'Information: "{content}"'
            }


    def search(self, user_topic=None,key_words = None, stock_name=None, stock_symbol=None):
        to_return = {}
        if user_topic and key_words:
            content = self.client.search(key_words, search_depth="basic", max_results=15)["results"]
            content = [x for x in content if len(x["content"].split()) <500]

            agent_query = user_topic
            messages = [self._get_system_context(), self._get_user_context(agent_query =agent_query, content= content)]

            response = self.openai_client.chat.completions.create(model="gpt-3.5-turbo-0125", temperature=0,messages=messages)
            response = response.choices[0].message.content
            try :
                to_save = json.loads(response)
            except json.JSONDecodeError:
                to_save = response
            to_return["topic_from_web"] =to_save

        if stock_name and stock_symbol:
            search_query = "Opinions about " + stock_name + "(" + stock_symbol + ")"
            content = self.client.search(search_query, search_depth="basic", max_results=15)["results"]
            content = [x for x in content if len(x["content"].split()) < 500]

            agent_query = "What is the sentiment of the given text. Pick one of the following: positive, negative, neutral, mixed, or not enough information."
            messages = [self._get_system_context(), self._get_user_context(agent_query=agent_query, content=content)]
            response = self.openai_client.chat.completions.create(model="gpt-3.5-turbo-0125", temperature=0,messages=messages)
            response = response.choices[0].message.content

            try:
                to_save = json.loads(response)
            except json.JSONDecodeError:
                to_save = response
            to_return["sentiment_from_web"] =to_save
        return to_return

