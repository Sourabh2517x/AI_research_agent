from agents import build_search_agent,build_reader_agent,writer_chain,critic_chain

def run_research_pipeline(topic:str) -> dict:
    
    state = {}
    
    # invoke search agent
    search_agent = build_search_agent()
    search_result = search_agent.invoke({"messages" : [("user", f"Find recent, reliable and detailed information about: {topic}")]})
    state["search_results"] = search_result['messages'][-2].content
    
    # invoke reader agent 
    reader_agent = build_reader_agent()
    reader_result = reader_agent.invoke({
        "messages": [("user",
            f"Based on the following search results about '{topic}', "
            f"pick the most relevant URL and scrape it for deeper content.\n\n"
            f"Search Results:\n{state['search_results']}"
        )]
    })
    state['scraped_content'] = reader_result['messages'][-1].content
    
    # invoke writer chain 
    research_combined = (
        f"SEARCH RESULTS : \n {state['search_results']} \n\n"
        f"DETAILED SCRAPED CONTENT : \n {state['scraped_content']}"
    )
    state["report"] = writer_chain.invoke({
        "topic" : topic,
        "research" : research_combined
    })
    
    # invoke critic report  
    state['feedback'] = critic_chain.invoke({
        "report":state['report']
    })
    
    return state


if __name__ == "__main__":
    topic = input("\n Enter a research topic : ")
    run_research_pipeline(topic)
    