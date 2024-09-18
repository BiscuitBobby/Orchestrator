from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_community.llms import LlamaCpp
from Secrets.keys import llama_path

callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

llm = LlamaCpp(
    model_path=llama_path,
    temperature=0.75,
    top_p=1,
    callback_manager=callback_manager,
    verbose=True,
)