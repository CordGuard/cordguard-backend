#from cordguard_consumer import consume_in_app_queue
import asyncio

# !Deprecated
def run_async_consumer():
    """
    Start the async queue consumer.
    
    This function creates a new event loop and runs the consume_in_app_queue
    coroutine to process files in the background.
    """
    # loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)
    # loop.run_until_complete(consume_in_app_queue())
    pass