import wolframalpha
from langchain_core.tools import tool
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from Secrets.keys import wolfram_app_id
from models.api import Gemini as llm
# from models.llama_3_8b import llm

app_id = wolfram_app_id
client = wolframalpha.Client(app_id)


class WebSearch:
    def scrape_google_search(self, query, n=5):
        # n = number of sites to scrape

        print('initializing...')

        info = []
        references = []
        self.driver = webdriver.Firefox()
        print('searching...')
        try:
            url = f"https://www.google.com/search?q={query}"
            self.driver.get(url)

            WebDriverWait(self.driver, 5).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.tF2Cxc'))
            )

            # Extract search results from the current page
            search_results = self.driver.find_elements("css selector", 'div.tF2Cxc')

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
                if len(references)>=n:
                    break

            info.append(references)

        except Exception as e:
            print(f"error: {e}")

        finally:
            # print(info)
            self.driver.quit()
            return references

    def llm_prompt(self, query, context=None):
        if context:
            prompt = f"""
                    Here is my query: {query},
                    answer while keeping in account the following information:{context.replace(':', '')}
                    """

        else:
            try:
                #prompt = f"Briefly answer the following query: {query}"
                prompt = f"""
                Briefly answer the following query: {query},
                Here are some related search results: {self.scrape_google_search(query)}
                """
            except:
                print("failed to scrape results")
                prompt = f"Briefly answer the following query: {query}"

        completion = llm.invoke(prompt)
        print(completion)

        return completion

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
        response = self.llm_prompt(query, context)
        return response


# -------------------------------------------------------------------------------------------------------------------
search_agent = WebSearch()

@tool(return_direct=True)
def CustomSearch(tool_input: str):
    """Useful for answering questions about future events, current affairs, positions of power, weather, details and events, browse the internet"""

    return f"{search_agent.search(tool_input)}\n"
