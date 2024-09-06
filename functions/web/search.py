import wolframalpha
from langchain_core.tools import BaseTool, tool
from langchain_google_genai import ChatGoogleGenerativeAI
from selenium import webdriver
from Secrets.keys import google_api, wolfram_app_id

llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", google_api_key=google_api)

app_id = wolfram_app_id
client = wolframalpha.Client(app_id)


class websearch:
    def __init__(self, model):
        self.model = model

    def scrape_google_search(self, query):
        print('initializing...')
        info = []
        references = []
        driver = webdriver.Firefox()
        print('searching...')
        try:
            url = f"https://www.google.com/search?q={query}"
            driver.get(url)

            # Extract search results from the current page
            search_results = driver.find_elements("css selector", 'div.tF2Cxc')

            # Extract data from each search result
            for result in search_results:
                description = ''
                title_element = result.find_element("css selector", 'h3')
                title = title_element.text

                url_element = result.find_element("css selector", 'a')
                url = url_element.get_attribute('href')

                description_element = result.find_element("css selector", 'div')
                description = f"{description}\n{description_element.text}"

                references.append(f"Title: {title}, URL: {url}, DESCRIPTION: {description}")

            info.append(references)

        except Exception as e:
            print(f"error: {e}")

        finally:
            # print(info)
            driver.quit()
            return references

    def llm_prompt(self, query, context=None):
        if context:
            prompt = f"""
                    Here is my query: {query},
                    answer while keeping in account the following information:{context.replace(':', '')}
                    """

        else:
            try:
                prompt = f"""
                    Here is my query: {query},
                    Here are some related search results: {self.scrape_google_search(query)}
                    """
            except:
                print("failed to scrape results")
                prompt = f"query: {query}"

        completion = self.model.invoke(prompt)

        print(completion)
        return completion.content

    def search_wolfram(self, query):
        try:
            res = client.query(query)
            answer = next(res.results).text
            print(f"{answer}\n\n")
        except:
            answer = None
        return answer

    def search(self, query):
        print('start')
        context = self.search_wolfram(query)
        print(context)
        response = f"**query**:\n{query}\n\n**response**:\n{self.llm_prompt(query, context)}"
        return response


# -------------------------------------------------------------------------------------------------------------------
search_agent = websearch(model=llm)

@tool
def CustomSearch(tool_input: str):
    """Useful for answering questions about future events, current affairs, positions of power, weather, details and events, browse the internet"""

    return f"\nObservation: \nsearch_input: {tool_input}\nsearch_agent: {search_agent.search(tool_input)}"
