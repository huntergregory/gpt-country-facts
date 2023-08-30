## dependencies
import os

from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.utilities import WikipediaAPIWrapper

from api.apikey import apikey
os.environ['OPENAI_API_KEY'] = apikey

## fact kinds
all_fact_kinds = [
    'random',
    'culture',
    'history',
    'geography',
    'food',
    'sports/games',
    'Star Wars',
]

## temperature
TEMPERATURE = 0.3

## prompt templates
LOCATION="""You are an expert at describing the relative location of a country. Your descriptions are brief. For the final country below, provide response similar to the other examples:
COUNTRY: United States of America
LOCATION: One of three countries in North America.

COUNTRY: Japan
LOCATION: Eastern Asian country near China.

COUNTRY: Israel
LOCATION: Middle Eastern country adjacent to the Mediterannean Sea.

COUNTRY: {country}
LOCATION: """

RANDOM_FUN_FACT = 'In one brief sentence, tell me a fact about the country of {country}.'
OTHER_FUN_FACT = 'In one brief sentence, tell me a fact about the country of {country}. The fact must be related to the topic of {fact_kind}.'
ARTICLE_PROMPT = """Please read the article below, and come up with a fact about the country of {country} based on the article.
ARTICLE: {research}

Using this article, """
RANDOM_FUN_FACT_RESEARCH = ARTICLE_PROMPT + RANDOM_FUN_FACT
OTHER_FUN_FACT_RESEARCH = ARTICLE_PROMPT + OTHER_FUN_FACT + "If the article does not mention anything about the topic of {fact_kind} related to the country of {country}, then you must say \"No mention of {fact_kind} in Wiki research for {country}\"."

def fact_prompt_template(fact_kind, use_wiki):
    if fact_kind == 'random':
        if use_wiki:
            return RANDOM_FUN_FACT_RESEARCH
        return RANDOM_FUN_FACT
    if use_wiki:
        return OTHER_FUN_FACT_RESEARCH
    return OTHER_FUN_FACT

## model
class Model:
    def __init__(self):
        print('initializing model with temperature {}'.format(TEMPERATURE))
        self._llm = OpenAI(temperature=TEMPERATURE)
        self._fact_kinds = []
        self._wiki = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=4000)
        self._use_wiki = False
        self._location_memory = ConversationBufferMemory(input_key='country', memory_key='chat_history', human_prefix='COUNTRY', ai_prefix='RESULT')
        self._current_research = []

    def set_fact_kinds(self, fact_kinds):
        self._fact_kinds = fact_kinds

    def set_use_wiki(self, v):
        self._use_wiki = v

    def get_country_facts(self, country):
        print('getting country facts for: {}'.format(country))
        facts = []
        self._current_research = []
        for fact_kind in self._fact_kinds:
            args = {'country': country}

            if self._use_wiki:
                search_term = country
                if fact_kind != 'random':
                    search_term = '{} {}'.format(search_term, fact_kind)

                print('researching for fact {}...'.format(fact_kind))
                research = self._wiki.run(search_term)
                print('finished research for fact {}...'.format(fact_kind))

                self._current_research.append(research)
                args['research'] = research

            if fact_kind != 'random':
                args['fact_kind'] = fact_kind

            template = PromptTemplate(input_variables=[k for k in args.keys()], template=fact_prompt_template(fact_kind, self._use_wiki))
            chain = LLMChain(llm=self._llm, prompt=template, verbose=True)

            print('getting fact {}...'.format(fact_kind))
            fact = chain.run(**args)
            print('got fact {}'.format(fact_kind))

            facts.append(fact)

        location = self._get_country_location(country)
        return location, facts

    def get_current_research(self):
        return self._current_research

    def get_location_memory(self):
        return self._location_memory.buffer

    # don't call into GPT if we already stored a response
    def _get_country_location(self, country):
        messages = self._location_memory.buffer_as_messages
        for i in range(0, len(messages)-1, 2):
            if messages[i].content == country:
                return messages[i+1].content

        location_template = PromptTemplate(input_variables=['country'], template=LOCATION)
        location_chain = LLMChain(llm=self._llm, prompt=location_template, verbose=True, output_key='location', memory=self._location_memory)
        print('getting location')
        location = location_chain.run(country=country)
        print('got location')
        return location

model = Model()
