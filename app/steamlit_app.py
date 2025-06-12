import streamlit as st
import os
import json


from langchain_core.prompts import ChatPromptTemplate
from openai import OpenAI

from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
from financial_data.financial_data import FinancialStatementsAnalysis
from internet_search.tavily_internet_search import TavilyInternetSearch

from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI

with st.sidebar:
    quadcode_hackathon_api_key = st.text_input("Quadcode Hackathon API key", type="password")
    st.write(
        "This app is powered by QUADCODE HACKA(I)THON 2024. Get your api key at hackathonsales@quadcode.com.")
    if quadcode_hackathon_api_key:
        if quadcode_hackathon_api_key == "hack2024":
            st.write("API key is correct.")
            openai_api_key = st.text_input("OpenAI API key", type="password")
            os.environ["OPENAI_API_KEY"] = openai_api_key
            openai_client = OpenAI()

            tavily_api_key = st.text_input("Tavily API key", type="password")
            os.environ["TAVILY_API_KEY"] = tavily_api_key
        else:
            st.write("API key is incorrect.")
            st.error("API key is incorrect.")
    else:
        st.write("Please enter your API key.")
        st.error("Please enter your API key.")

# Initialize chat history
def _initialize_chat_history():
    if "messages" not in st.session_state:
        st.session_state.messages = []
        return True
    return False

def _add_message_to_chat_history(role: str, content):
    st.session_state.messages.append({"role": role, "content": content})

def _display_chat_messages(role_avatars: dict):
    to_return = False
    for message in st.session_state.messages:
        to_return = True
        with st.chat_message(name=message["role"], avatar=role_avatars[message["role"]]):
            st.markdown(message["content"])
    return to_return


def _process_user_input(user_input):
    openai_client = OpenAI()
    prompt = """You are a language model that processes a user's input and extracts information from it.
    Your output should strictly be a list of JSON objects, each containing 4 fields: "user_topic", "key_words", "stock_name" and "stock_symbol", 
    only if you can identify any of these fields from the user's input, else don't include them.
    Do not include any stock name and symbol information in the field "user_topic" and "key_words"
    and do not include any topic-related information in the field "stock_name" and "stock_symbol"".
    In addition, if there is more than one stock identified, provide a list of JSON objects, one for each stock.
    Finally, if the user input is not related to the financial domain, you should return an empty list.
    
    For example, if the user input is "What is the intrinsic value of a company?",
    you should only include "user_topic": "How to find intrinsic value of a company" and 
    "key_words": "intrinsic value of a company, value investor"

    An other example, if the user input is "Analyse the latest financial statements of Ardelyx, Inc. and Microsoft in quarter basis?",
    you should include two JSON objects, one for each stock.
    The first json object should include "user_topic": "How to analyse financial statements",
    "key_words": "fundamentals of a stock, financial statements",
    "stock_name": "Ardelyx, Inc.", "stock_symbol": "ARDX".
    The second json object should include "user_topic": "How to analyse financial statements",
    "key_words": "fundamentals of a stock, financial statements",
    "stock_name": "Microsoft Corporation", "stock_symbol": "MSFT"."""
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": user_input},
    ]
    llm_output = openai_client.chat.completions.create(model="gpt-4o", temperature=0, messages=messages)
    llm_output = llm_output.choices[0].message.content

    try:
        to_return = json.loads(llm_output)
    except json.JSONDecodeError:
        to_return = llm_output
    return to_return

def _get_chatbot_response_for_premium_user():
    prompt = """You are part of our company's SaaS - Software as a Service product which is a helpful AI language model financial assistant.
    Our SaaS service supports and aids financial decisions through lean but to the point financial analysis over the fundamentals.
    Our current free pricing plan doesn't not include the analysis of more than one stock at a time,
    nor providing detailed statistics over internet search, not provided detailed analysis on financial statements.
    Your task is to inform the user when asks for premium plan about the limitations of the free plan in a polite and professional manner
     and offer the premium plan."""
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": "Provide detailed analysis over internet search and financial statements"},
    ]
    llm_output = openai_client.chat.completions.create(model="gpt-3.5-turbo-0125", temperature=0.9, messages=messages)
    return llm_output.choices[0].message.content


def _get_chatbot_response_for_dataframes(financial_ratios):
    prompt = f"""You are a helpful AI language model financial assistant.
    You always response in a clean, clear and to the point manner and speak only for the stuff that you have high degree of confidence.
    You will be provided with:
    Financial ratios of the stock, A : Efficiency, B: Solvency, C: Management Performance Ratios ,
    
    What is the financial analysis over the fundamentals to determine the intrinsic value of a company and its performance over time? 
     """

    agent = create_pandas_dataframe_agent(
        ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613"),
        financial_ratios,
        verbose=True,
        agent_type=AgentType.OPENAI_FUNCTIONS,
        allow_dangerous_code=True
    )
    to_return = agent.invoke(prompt)
    return to_return

def _get_chatbot_response_for_text(question, constructed_context=None):
    chatbot_role = """You are a helpful AI language model financial assistant for stocks.
     Your job is to support and aid financial decisions by highlighting important news about the stock 
     and providing opinion mining and recommendations regarding a stock from the internet.
     
     You will be provided with:
     1 recent news (field "topic_from_web") containing the refined internet search results of a user's query
     2 opinion mining (field "sentiment_from_web") containing the refined internet search results of what people write about a stock
     3 what yahoo finance suggests (field "yahoo_recommendations") for a stock,

        
     If you are not asked to do something relevant to your job, response in a polite manner of your job and your capabilities.
     If you are asked to provide a financial assistance on a stock but you are missing any of the items 1 and 2 from the context,
     state that you couldn't retrieve them and continue analysis with what you have.
     If you are asked to provide a financial assistance highlight in a marketing style that our premium plan offers 
     comprehensive stock analysis, including:
     Industry Comparison: Evaluate stocks by industry for deeper insights.
     S&P Comparison analysis: Access both fundamental and technical analysis of the S&P 500, ensuring a well-rounded understanding of market trends.
     
     Always response in a lean, clean and clear manner and speak only for the stuff that you have high degree of confidence."""


    llm = ChatOpenAI(model="gpt-4", temperature=0.5)
    if constructed_context:
        template = chatbot_role + """ Answer the following user's input based on this context:
        {constructed_context}

        User's input: {question}
        """
        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | llm
        to_return = chain.invoke({"constructed_context": str(constructed_context), "question": question})
    else:
        template = chatbot_role + """ Answer the following user's input: {question}"""
        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | llm
        to_return = chain.invoke({"question": question})
    return to_return


def _display_stock_data(stock_symbol, financial_ratios, historical_prices, capitalization, recommendations):

    # Display market capitalization
    st.write(f"##  {stock_symbol} - Current Market Capitalization")
    st.write(f"{capitalization:,}")

    # Display historical prices
    st.write("Historical Prices")
    st.line_chart(historical_prices['Close'])

    # Display recommendations
    st.write(f"## Yahoo Recommendations")
    st.write(recommendations)

    # Display financial ratios
    st.write(f"## {stock_symbol} Financial Ratios")
    st.write(financial_ratios)

def main_app(starting_role="user"):
    st.title("Quadcode HackA(I)thon 2024 - Financial Assistant App")
    role = starting_role

    role_avatars = {"user": "👤", "assistant": "🤖"}

    _ = _initialize_chat_history()
    _ = _display_chat_messages(role_avatars)

    # React to user input
    user_input = st.chat_input()
    # user_input = "What do you think about microsoft stock?"
    if user_input:
        role = "user"
        with st.chat_message(role, avatar=role_avatars[role]):
            st.markdown(user_input)
        _add_message_to_chat_history(role, user_input)

        role = "assistant"
        processed_user_input = _process_user_input(user_input)
        if len(processed_user_input) > 1:
            chatbot_response = _get_chatbot_response_for_premium_user()
        elif len(processed_user_input) < 1:
            chatbot_response = _get_chatbot_response_for_text(user_input)
        else:
            constructed_context = processed_user_input[0]
            user_topic = constructed_context["user_topic"]
            key_words = constructed_context["key_words"]
            stock_name = constructed_context.get("stock_name")
            stock_symbol = constructed_context.get("stock_symbol")

            if stock_symbol:
                financial_statement_analysis = FinancialStatementsAnalysis(stock_symbol)
                financial_ratios = financial_statement_analysis.get_financial_ratios()
                financial_ratios.rename(columns=financial_statement_analysis.get_financial_ratios_definition(), inplace=True)
                historical_prices = financial_statement_analysis.get_historical_prices()
                current_capitalization = financial_statement_analysis.get_current_capitalization()
                recommendations = financial_statement_analysis.get_recommendations()
                _display_stock_data(stock_symbol, financial_ratios, historical_prices, current_capitalization, recommendations)
                constructed_context.update(
                    {"current_capitalization": current_capitalization, "yahooo_recommendations": recommendations,
                     })

            # if not financial_ratios.empty and not historical_prices.empty:
            #     chatbot_response = _get_chatbot_response_for_dataframes(financial_ratios)
            #     response = f"{chatbot_response.content}"
            #     with st.chat_message(role, avatar=role_avatars[role]):
            #         st.markdown(response)
            #         _add_message_to_chat_history(role, response)

            tavily_search = TavilyInternetSearch(tavily_api_key)
            tavily_search_result = tavily_search.search(user_topic=user_topic, key_words=key_words, stock_name=stock_name,
                                                       stock_symbol=stock_symbol)
            constructed_context.update(tavily_search_result)
            chatbot_response = _get_chatbot_response_for_text(question=user_input, constructed_context=constructed_context)

        response = f"{chatbot_response.content}"
        with st.chat_message(role, avatar=role_avatars[role]):
            st.markdown(response)
        _add_message_to_chat_history(role, response)



if __name__ == "__main__":
    main_app()
