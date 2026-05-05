"""Base LangGraph Agent for StepIn"""
import os
import logging
from typing import Optional, Dict, Any, List, Callable
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from app.agents.state import AgentState, get_default_state
from app.services.gemini_service import gemini_service

logger = logging.getLogger(__name__)


class BaseAgent:
    """
    Base class for all LangGraph agents in StepIn.
    
    Provides common functionality:
    - State management
    - Gemini API integration
    - Error handling
    - Logging
    """
    
    def __init__(
        self,
        name: str,
        system_prompt: str,
        model: str = "gemini-2.5-flash",
        temperature: float = 0.7,
    ):
        self.name = name
        self.system_prompt = system_prompt
        self.model = model
        self.temperature = temperature
        self.graph: Optional[StateGraph] = None
        
        logger.info(f"Initialized {name} agent with model {model}")
    
    async def generate(
        self,
        state: AgentState,
        prompt: str,
        require_json: bool = False,
    ) -> str:
        """
        Generate content using Gemini API.
        
        Args:
            state: Current agent state
            prompt: User prompt
            require_json: Whether to parse response as JSON
            
        Returns:
            Generated text or parsed JSON
        """
        try:
            if require_json:
                result = await gemini_service.generate_json(
                    prompt=prompt,
                    model=self.model,
                    system_instruction=self.system_prompt,
                    temperature=self.temperature,
                )
                return result
            else:
                result = await gemini_service.generate_content(
                    prompt=prompt,
                    model=self.model,
                    system_instruction=self.system_prompt,
                    temperature=self.temperature,
                )
                return result
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            state["error"] = str(e)
            raise
    
    def create_node(self, func: Callable) -> Callable:
        """
        Decorator to create a LangGraph node from a function.
        
        The function should accept state and return updated state.
        """
        async def node_wrapper(state: AgentState) -> AgentState:
            try:
                result = await func(self, state)
                return result
            except Exception as e:
                logger.error(f"Error in node {func.__name__}: {e}")
                state["error"] = str(e)
                return state
        return node_wrapper
    
    def add_nodes(self, graph: StateGraph, nodes: Dict[str, Callable]) -> None:
        """Add nodes to the graph"""
        for name, func in nodes.items():
            graph.add_node(name, self.create_node(func))
    
    def compile(self) -> StateGraph:
        """Compile the graph - must be implemented by subclass"""
        if self.graph is None:
            self.graph = StateGraph(AgentState)
        return self.graph.compile()
    
    async def run(self, initial_state: Dict[str, Any]) -> AgentState:
        """
        Run the agent with initial state.
        
        Args:
            initial_state: Initial state dictionary
            
        Returns:
            Final state after graph execution
        """
        # Merge with default state
        state = get_default_state()
        state.update(initial_state)
        
        if self.graph is None:
            self.compile()
        
        # Invoke the graph
        try:
            result = await self.graph.ainvoke(state)
            return result
        except Exception as e:
            logger.error(f"Error running agent {self.name}: {e}")
            state["error"] = str(e)
            return state


class StructuredOutputAgent(BaseAgent):
    """
    Agent that outputs structured JSON.
    
    Use when you need the LLM to return specific JSON schemas.
    """
    
    def __init__(
        self,
        name: str,
        system_prompt: str,
        output_schema: Dict[str, Any],
        model: str = "gemini-2.5-flash",
        temperature: float = 0.7,
    ):
        super().__init__(name, system_prompt, model, temperature)
        self.output_schema = output_schema
    
    def get_schema_prompt(self) -> str:
        """Generate prompt with output schema"""
        import json
        schema_str = json.dumps(self.output_schema, indent=2)
        return f"""
{self.system_prompt}

OUTPUT SCHEMA:
```json
{schema_str}
```

Respond with valid JSON only, no other text or explanation.
"""


def create_agent_node(agent: BaseAgent, node_name: str):
    """
    Factory to create a node function from an agent method.
    
    Usage:
        graph.add_node("extract_diary", create_agent_node(diary_agent, "extract"))
    """
    async def node(state: AgentState) -> AgentState:
        method = getattr(agent, node_name, None)
        if method is None:
            raise ValueError(f"Agent {agent.name} has no method {node_name}")
        return await method(state)
    return node