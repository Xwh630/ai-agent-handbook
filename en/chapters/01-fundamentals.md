# Chapter 1: AI Agent Fundamentals

> In this chapter, you'll understand what an AI Agent is, why it matters, and how it fundamentally works.

---

## 1.1 What is an AI Agent?

### Traditional LLM Call vs Agent

**Traditional LLM call:**
```
User question → LLM processes → Return answer
```

**AI Agent:**
```
User goal → [Perceive → Decide → Act → Observe] loop → Goal achieved
              ↓
      Call tools / Query memory / Collaborate with other Agents
```

### Core Components of an Agent

A complete Agent = **LLM + Persona + Tools + Memory + Decision Logic**

| Component | Role | Analogy |
|-----------|------|---------|
| **LLM (Brain)** | Understand, reason, generate | Human brain |
| **Persona** | Defines domain expertise and behavior | Professional identity |
| **Tools** | External capabilities (search, compute, databases) | Hands and tools |
| **Memory** | Short-term conversation + long-term knowledge | Memory system |
| **Decision Logic** | Rules that determine the next action | Decision center |

---

## 1.2 The Agent Loop

At its core, an Agent is a while loop that repeatedly executes these steps:

```python
def agent_loop(user_goal: str, tools: dict, max_steps: int = 10):
    messages = [{"role": "system", "content": build_system_prompt(tools)}]
    messages.append({"role": "user", "content": user_goal})
    
    for step in range(max_steps):
        # 1. Perceive: call the LLM to get a response
        response = call_llm(messages)
        messages.append({"role": "assistant", "content": response})
        
        # 2. Parse: check whether a tool needs to be called
        action = parse_action(response)
        
        if action is None:
            # No tool call, return the final answer
            return response["content"]
        
        # 3. Act: execute the tool call
        tool_result = execute_tool(action.name, action.parameters)
        messages.append({
            "role": "tool",
            "tool_call_id": action.id,
            "content": tool_result
        })
        # 4. Observe: the LLM continues reasoning based on tool results
    
    return "Task timeout, please simplify your request"
```

### The ReAct Pattern: Reasoning + Acting

ReAct = **Re**asoning + **Act**ing

```
Thought: I need to check the weather first, then calculate the travel budget
Action: get_weather(city="Beijing")
Observation: Beijing is sunny today, 25°C
Thought: The weather is great, I can continue planning the itinerary...
Action: calculate_budget(days=3, location="Beijing")
...
Final Answer: A 3-day Beijing trip budget is approximately 5000 RMB
```

---

## 1.3 Why Do We Need Agents?

### Limitations of a Single LLM

| Problem | Example |
|---------|---------|
| **Knowledge cutoff** | LLM training data has a cutoff date |
| **Factual accuracy** | Prone to hallucination |
| **Complex tasks** | Tasks requiring multi-step reasoning and tool calls |
| **Personalization** | Cannot remember user preferences and history |

### The Value Agents Bring

```
┌─────────────────────────────────────────────┐
│              Traditional LLM                 │
│  Q&A → Generate → Done                       │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│              AI Agent                        │
│  Understand goal → Plan → Execute → Verify → Adjust
│       ↑                                      │
│       └── Loop and optimize until success ───┘
└─────────────────────────────────────────────┘
```

---

## 1.4 Multi-Agent vs Single-Agent Systems

### Single-Agent Architecture

```
User → [Agent A] → Result
```

**Pros:** Simple, fast, low cost
**Cons:** Struggles with complex tasks, easy to drift off target

### Multi-Agent Architecture

```
                    ┌──────────────┐
                    │   Supervisor │
                    └──────┬───────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
    ┌─────▼─────┐   ┌─────▼─────┐   ┌─────▼─────┐
    │  Research │   │   Writer  │   │  Reviewer │
    │   Agent   │   │   Agent   │   │   Agent   │
    └───────────┘   └───────────┘   └───────────┘
```

**Pros:** Specialized division of labor, parallel execution, easier debugging
**Cons:** High coordination complexity, more token consumption

---

## 1.5 Key Terms Cheat Sheet

| Term | Definition |
|------|------------|
| **Agent** | An LLM entity with perceive-decide-act capabilities |
| **Tool Calling** | The Agent's ability to call external tools |
| **Function Calling** | Interacting with external tools via function call interfaces |
| **RAG** | Retrieval-Augmented Generation |
| **Orchestration** | Controlling execution order and data flow of multiple agents |
| **Handoff** | One agent transfers control to another agent |
| **MCP** | Model Context Protocol, standardized AI tool protocol |
| **A2A** | Agent-to-Agent Protocol, inter-agent communication protocol |
| **Checkpointer** | Saves agent state for resumable execution |
| **HITL** | Human-in-the-Loop, human review mechanism |

---

## 1.6 Chapter Summary

- An Agent is not a simple LLM call, but an intelligent system with a perceive-decide-act loop
- Core components: LLM + Persona + Tools + Memory + Decision
- The ReAct pattern is the classic model of agent reasoning and acting
- Multi-agent systems suit complex tasks, but coordination costs are high
- When choosing, consider task complexity, budget, and team tech stack

---

## Next Chapter

[→ Chapter 2: Build a ReAct Agent from Scratch](./02-reaact-from-scratch.md)
