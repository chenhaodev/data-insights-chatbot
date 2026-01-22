# Fix: Agent Not Following Through on Visualization Requests

## Date
2026-01-23

## Problem

User reported that the agent didn't follow their explicit instruction to create visualizations:

**Conversation Flow:**
1. Agent: "Would you like me to create visualizations of these distributions?"
2. User: "oh yes, please create visualizations of these distributions"
3. Agent: "I'd be happy to create visualizations... Could you please tell me which columns?"
4. User: "all data, all columns"
5. Agent: [Provided text overview instead of calling create_visualization tool] ❌

**Expected Behavior:**
- Agent should have called `create_visualization` tool after user said "yes"
- When user clarified "all columns", should have created distributions for key numeric columns

**Root Cause:**
- Agent was over-cautious and asked too many clarifying questions
- Did not execute the tool even when user gave explicit approval
- Responded with text description instead of taking action

## Solution

Added **ACTION-ORIENTED BEHAVIOR** guidelines to `agent/prompts.py`:

### 1. Execute Immediately on User Approval

```
- When user explicitly says "yes", "ok", "please do it", "go ahead"
  → EXECUTE IMMEDIATELY, don't ask more questions
- If user agrees to create visualizations
  → call create_visualization tool RIGHT AWAY
- NEVER respond with just text/overview when user explicitly requested visualizations
```

### 2. Handle "All Columns" Requests

```
- When user says "all columns" or "all data" for distributions
  → create distribution plots for key numeric columns (pick 3-5 most important ones)
- For "all columns" request: Call create_visualization multiple times
  (once per column) for the most relevant numeric columns
```

### 3. Bias Toward Action

```
- Bias toward ACTION over clarification when user intent is clear
- When in doubt between describing and doing → DO IT (call the tool)
- "User wants to see X" → call create_visualization, don't just explain X
- CRITICAL: If user explicitly requests visualizations and you respond
  without calling create_visualization tool, you have FAILED the task
```

### 4. Special Cases for Visualizations

```
- User wants "distribution of all columns"
  → Create distributions for 3-5 most important numeric columns
  OR suggest using generate_profile_report for comprehensive view

- User wants "see all data visually"
  → Start with correlation heatmap, then offer specific distributions

- User says "yes" to your visualization suggestion
  → IMMEDIATELY call create_visualization, don't ask more questions
```

### 5. Updated Key Principles

```
**Key Principles**:
1. Start simple, earn trust, then gradually increase analytical depth
2. BUT: Always execute immediately when user gives clear instructions or says "yes"
3. Gradual proactivity applies to SUGGESTIONS and HYPOTHESES,
   not to EXECUTION of user requests
```

## Changes Made

**File:** `agent/prompts.py`

**Sections Added/Modified:**

1. **ACTION-ORIENTED BEHAVIOR (CRITICAL)** - New section (~10 lines)
2. **Special Cases for Visualizations** - New subsection (~6 lines)
3. **Key Principles** - Updated from 1 principle to 3
4. **Important Rules** - Added 3 critical rules about tool execution

**Total:** ~20 lines added/modified

## Expected Behavior After Fix

### Scenario 1: Direct Agreement

```
Agent: "Would you like me to create visualizations?"
User: "yes"
Agent: [Immediately calls create_visualization for relevant columns]
      [Shows the visualizations]
      "Here are the distribution plots for Sales_Price, Active_Subscriptions,
       and Original_Price..."
```

### Scenario 2: "All Columns" Request

```
User: "show me distributions of all columns"
Agent: [Calls create_visualization multiple times OR suggests heatmap first]
      [Shows visualizations]
      "I've created distribution plots for the key numeric columns:
       Sales_Price, Active_Subscriptions, Original_Price, Fee_Level, and Duration_Days.

       Would you like to see distributions for the remaining columns as well?"
```

### Scenario 3: No Over-Asking

```
User: "create a scatter plot of X vs Y"
Agent: [Immediately calls create_visualization(plot_type='scatter', x_col='X', y_col='Y')]
      [Shows visualization]
      [NO asking "which X?" or "are you sure?" - just does it]
```

## Key Distinction

**Gradual Proactivity applies to:**
- ✅ How many hypotheses to provide
- ✅ How many follow-up questions to ask
- ✅ Depth of interpretation

**Gradual Proactivity does NOT apply to:**
- ❌ Executing explicit user requests
- ❌ Taking action when user says "yes"
- ❌ Creating visualizations when user clearly wants them

## Philosophy

**From:** "Let me understand exactly what you want before I do anything"
**To:** "You told me what you want - let me do it now"

The agent should:
- **Ask questions** when suggesting proactive next steps
- **Take action** when user has already made their intent clear
- **Bias toward doing** over describing when visualization is requested

---

**Status:** ✅ Fixed and ready for testing
**Testing:** Restart Streamlit and try the same conversation flow
**Expected:** Agent will now call create_visualization tool when you say "yes"
