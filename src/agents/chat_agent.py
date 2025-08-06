import logging
from typing import Dict, Any, List, TypedDict
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from src.agents.search_agent import SearchAgent
from src.agents.document_agent import DocumentAgent
from src.utils.memory_manager import ConversationMemoryManager
from src.config.settings import settings

logger = logging.getLogger(__name__)

class ChatState(TypedDict):
    query: str
    response: str
    chat_history: str
    needs_search: bool
    needs_documents: bool
    search_results: Dict[str, Any]
    document_results: Dict[str, Any]
    final_response: str
    sources: List[Dict[str, Any]]

class ChatAgent:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.memory_manager = ConversationMemoryManager(session_id)
        self.search_agent = SearchAgent()
        self.document_agent = DocumentAgent()
        self.llm = ChatOpenAI(
            openai_api_key=settings.openai_api_key,
            model_name=settings.llm_model,
            temperature=settings.temperature
        )
        # Build the conversation graph
        self.graph = self._build_graph()
        # Routing prompt
        self.routing_prompt = PromptTemplate(
            input_variables=["query", "chat_history", "has_documents"],
            template=""" Analyze the user's query and determine what actions are needed.
            Chat History: {chat_history}
            User Query: {query}
            Available Documents: {has_documents}

            Determine if the query needs:
            1. Internet search (for current information, facts, news, general knowledge)
            2. Document search (for information from uploaded documents)
            3. Direct response (for casual conversation, greetings, simple questions)

            Respond with exactly one of: "SEARCH", "DOCUMENTS", "DIRECT", "BOTH"
            Decision: """
        )
        # Final response prompt
        self.final_prompt = PromptTemplate(
            input_variables=["query", "chat_history", "search_info", "document_info"],
            template=""" You are a helpful AI assistant. Based on the information gathered, provide a comprehensive response to the user's query.
            Chat History: {chat_history}
            User Query: {query}
            Search Information: {search_info}
            Document Information: {document_info}

            Provide a helpful, accurate, and well-structured response. If you used multiple sources, integrate the information coherently. Always be honest about the limitations of your knowledge.
            Response: """
        )

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph conversation flow."""
        def route_query(state: ChatState) -> str:
            """Determine the appropriate action based on the query."""
            try:
                has_docs = self.document_agent.has_documents()
                prompt = self.routing_prompt.format(
                    query=state["query"],
                    chat_history=state["chat_history"],
                    has_documents=has_docs
                )
                decision = self.llm.invoke(prompt).content.strip().upper()
                if "SEARCH" in decision:
                    return "search"
                elif "DOCUMENTS" in decision:
                    return "documents"
                elif "BOTH" in decision:
                    return "both"
                else:
                    return "direct"
            except Exception as e:
                logger.error(f"Error in routing: {str(e)}")
                return "direct"

        def search_node(state: ChatState) -> ChatState:
            """Perform internet search."""
            try:
                search_results = self.search_agent.search_and_respond(state["query"])
                state["search_results"] = search_results
                state["needs_search"] = True
                return state
            except Exception as e:
                logger.error(f"Error in search node: {str(e)}")
                state["search_results"] = {"success": False, "response": "Search failed"}
                return state

        def document_node(state: ChatState) -> ChatState:
            """Query documents."""
            try:
                doc_results = self.document_agent.query_documents(
                    state["query"], state["chat_history"]
                )
                state["document_results"] = doc_results
                state["needs_documents"] = True
                return state
            except Exception as e:
                logger.error(f"Error in document node: {str(e)}")
                state["document_results"] = {"success": False, "response": "Document query failed"}
                return state

        def both_node(state: ChatState) -> ChatState:
            """Perform both search and document query."""
            state = search_node(state)
            state = document_node(state)
            return state

        def direct_response_node(state: ChatState) -> ChatState:
            """Generate direct response without external sources."""
            try:
                direct_prompt = f""" Based on the conversation history, provide a helpful response to the user's query.
Chat History: {state["chat_history"]}
User Query: {state["query"]}
Response: """
                response = self.llm.invoke(direct_prompt)
                state["final_response"] = response.content.strip()
                state["sources"] = []
                return state
            except Exception as e:
                logger.error(f"Error in direct response: {str(e)}")
                state["final_response"] = "I apologize, but I encountered an error processing your request."
                return state

        def combine_results_node(state: ChatState) -> ChatState:
            """Combine results from different sources."""
            try:
                search_info = ""
                document_info = ""
                sources = []
                if state.get("search_results", {}).get("success"):
                    search_info = state["search_results"]["response"]
                    sources.extend(state["search_results"].get("sources", []))
                if state.get("document_results", {}).get("success"):
                    document_info = state["document_results"]["response"]
                    sources.extend(state["document_results"].get("sources", []))

                if not search_info and not document_info:
                    return direct_response_node(state)

                prompt = self.final_prompt.format(
                    query=state["query"],
                    chat_history=state["chat_history"],
                    search_info=search_info,
                    document_info=document_info
                )
                response = self.llm.invoke(prompt)
                state["final_response"] = response.content.strip()
                state["sources"] = sources
                return state
            except Exception as e:
                logger.error(f"Error combining results: {str(e)}")
                return direct_response_node(state)

        # Build the graph
        workflow = StateGraph(ChatState)
        
        # Add nodes
        workflow.add_node("search", search_node)
        workflow.add_node("documents", document_node)
        workflow.add_node("both", both_node)
        workflow.add_node("direct", direct_response_node)
        workflow.add_node("combine", combine_results_node)
        
        # Set conditional entry point
        workflow.set_conditional_entry_point(
            route_query,
            {
                "search": "search",
                "documents": "documents",
                "both": "both",
                "direct": "direct"
            }
        )
        
        # Add edges to combine or end
        workflow.add_edge("search", "combine")
        workflow.add_edge("documents", "combine")
        workflow.add_edge("both", "combine")
        workflow.add_edge("direct", END)
        workflow.add_edge("combine", END)
        
        return workflow.compile()

    def chat(self, query: str) -> Dict[str, Any]:
        """Process user query through the conversation graph."""
        try:
            logger.info(f"Processing query for session {self.session_id}: {query}")
            # Get conversation history
            chat_history = self.memory_manager.get_formatted_history()
            
            # Create initial state
            initial_state: ChatState = {
                "query": query,
                "response": "",
                "chat_history": chat_history,
                "needs_search": False,
                "needs_documents": False,
                "search_results": {},
                "document_results": {},
                "final_response": "",
                "sources": []
            }
            
            # Run the graph
            result = self.graph.invoke(initial_state)
            
            # Extract final response and sources
            final_response = result.get("final_response", "I apologize, but I couldn't process your request.")
            sources = result.get("sources", [])
            
            # Update memory
            self.memory_manager.add_user_message(query)
            self.memory_manager.add_ai_message(final_response)
            
            logger.info(f"Generated response for session {self.session_id}")
            return {
                "success": True,
                "response": final_response,
                "sources": sources,
                "session_id": self.session_id
            }
        except Exception as e:
            logger.error(f"Error in chat processing: {str(e)}")
            return {
                "success": False,
                "response": f"I encountered an error: {str(e)}",
                "sources": [],
                "session_id": self.session_id
            }

    def clear_conversation(self):
        """Clear conversation memory."""
        self.memory_manager.clear_memory()
        logger.info(f"Cleared conversation for session {self.session_id}")

    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get summary of current conversation."""
        return self.memory_manager.get_session_summary()