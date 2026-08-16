# Forge-core

**An independent AI platform for business solutions and AI integration, featuring a comprehensive marketing AI agent.**

## Overview

Forge-core is a modular, extensible AI platform designed for business solutions with a focus on marketing automation. The platform provides a complete framework for building intelligent agents with advanced capabilities in memory management, reasoning, task execution, tool management, security, module extensibility, and comprehensive auditing.

## Core Architecture

The platform is built around seven core components:

### 1. Memory System
- **Short-term Memory**: Session-based context storage with TTL
- **Long-term Memory**: Persistent SQLite-based storage
- **Vector Store**: Semantic search and retrieval capabilities
- **Memory Consolidation**: Automatic transfer from short-term to long-term storage

### 2. Reasoning Engine
- **Decision Making**: Multi-step reasoning with different modes (sequential, parallel, hierarchical, creative)
- **Planning**: Strategic goal decomposition and task planning
- **Context Analysis**: Understanding and processing context information
- **Evaluation**: Plan feasibility and quality assessment

### 3. Task Management
- **Task Queue**: Priority-based scheduling with dependency management
- **Task Executor**: Parallel execution with timeout and retry handling
- **Dependency Graph**: Complex task dependency resolution
- **Task Monitoring**: Real-time status tracking and failure handling

### 4. Tool Management
- **Tool Registry**: Dynamic tool registration and discovery
- **Tool Executor**: Safe execution with sandboxing options
- **Permission System**: Fine-grained access control
- **Execution History**: Comprehensive tracking and analytics

### 5. Security Layer
- **Authentication**: JWT-based user authentication
- **Authorization**: Role-based access control (RBAC)
- **Encryption**: Data encryption at rest and in transit
- **Security Audit**: Comprehensive security event logging

### 6. Module Management
- **Module Registry**: Dynamic module loading and discovery
- **Module Loader**: Load modules from files, directories, or packages
- **Module Sandbox**: Isolated execution environment
- **Dependency Management**: Complex dependency resolution

### 7. Auditing System
- **Event Logger**: Comprehensive event tracking for audit trails
- **Performance Monitor**: System performance metrics and monitoring
- **Error Tracker**: Error analysis and pattern recognition
- **Compliance Reporter**: Regulatory compliance reporting

## Marketing AI Agent

The platform includes a specialized marketing AI agent that integrates all core systems with marketing-specific functionality:

### Marketing Components
- **Content Generator**: AI-powered content creation for blogs, social media, emails
- **Campaign Manager**: End-to-end campaign creation and management
- **Audience Analyzer**: Advanced audience segmentation and insights
- **Performance Tracker**: Comprehensive marketing analytics and ROI tracking

### Marketing Capabilities
- Automated content generation across multiple channels
- Campaign planning and execution with task automation
- Audience segmentation and behavioral analysis
- Real-time performance tracking and optimization
- Multi-channel campaign coordination

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/MutantSqr/Forge-core.git
cd Forge-core

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```python
from marketing import MarketingAgent

# Initialize the marketing agent
agent = MarketingAgent(
    config={
        "memory_path": "./marketing_memory",
        "module_path": "./marketing_modules",
        "max_workers": 4
    },
    enable_security=True,
    enable_auditing=True
)

# Plan a marketing strategy
strategy = agent.plan_marketing_strategy(
    business_goals=["increase_brand_awareness", "generate_leads"],
    target_audience={"demographics": {"ages": [25, 35, 45], "locations": ["US", "UK"]}}
)

# Execute marketing tasks
result = agent.execute_marketing_task(
    task_description="Generate blog post about AI marketing",
    parameters={
        "action_type": "generate_content",
        "content_type": "blog_post",
        "topic": "AI in modern marketing",
        "tone": "professional"
    }
)

# Get marketing insights
insights = agent.get_marketing_insights(time_period="7d")

# Get agent status
status = agent.get_agent_status()

# Shutdown when done
agent.shutdown()
```

### Content Generation

```python
from marketing import ContentGenerator
from core.memory import MemorySystem
from core.tool import ToolManager

# Initialize components
memory = MemorySystem()
tool_manager = ToolManager()
content_gen = ContentGenerator(memory, tool_manager)

# Generate blog post
blog_post = content_gen.generate_blog_post(
    topic="Digital marketing trends 2024",
    tone="professional",
    length=1500,
    keywords=["AI", "automation", "personalization"]
)

# Generate social media post
social_post = content_gen.generate_social_media_post(
    platform="linkedin",
    topic="Business automation benefits",
    hashtags=["#automation", "#business", "#efficiency"]
)
```

### Campaign Management

```python
from marketing import CampaignManager
from core.memory import MemorySystem
from core.task import TaskManager

# Initialize components
memory = MemorySystem()
task_manager = TaskManager()
campaign_mgr = CampaignManager(memory, task_manager)

# Create campaign
campaign = campaign_mgr.create_campaign(
    name="Q4 Brand Awareness",
    goals=["increase_brand_recognition", "expand_reach"],
    channels=["social_media", "content_marketing", "email"],
    start_date=datetime.now() + timedelta(days=1),
    end_date=datetime.now() + timedelta(days=30),
    budget={"social_media": 5000, "content": 3000, "email": 2000}
)

# Launch campaign
campaign_mgr.launch_campaign(campaign["campaign_id"])

# Update metrics
campaign_mgr.update_campaign_metrics(
    campaign["campaign_id"],
    {"impressions": 15000, "clicks": 500, "conversions": 50}
)
```

## Architecture

```
Forge-core
│
├── Core Layer
│   ├── Memory System (short-term, long-term, vector)
│   ├── Reasoning Engine (planning, decision making, context analysis)
│   ├── Task Management (queue, executor, dependencies)
│   ├── Tool Management (registry, executor, sandbox)
│   ├── Security Layer (auth, authorization, encryption)
│   ├── Module Management (registry, loader, sandbox)
│   └── Audit System (events, performance, errors, compliance)
│
├── Marketing Layer
│   ├── Marketing Agent (main orchestration)
│   ├── Content Generator (AI content creation)
│   ├── Campaign Manager (campaign lifecycle)
│   ├── Audience Analyzer (segmentation & insights)
│   └── Performance Tracker (analytics & ROI)
│
└── Application Layer
    ├── Business Integration
    ├── Custom Extensions
    └── API Layer (future)
```

## Testing

The platform includes comprehensive test coverage:

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=core --cov=marketing --cov-report=html

# Run specific test file
pytest tests/test_memory_system.py -v
```

## CI/CD

The platform uses GitHub Actions for continuous integration:

- **Python CI**: Automated testing on Python 3.11 and 3.12
- **Code Coverage**: Coverage reporting with Codecov
- **Linting**: Code quality checks with flake8

## Configuration

### Memory Configuration
```python
memory = MemorySystem(
    storage_path="./memory_data",
    short_term_max_items=1000,
    short_term_ttl_hours=24
)
```

### Security Configuration
```python
security = SecurityManager(
    secret_key="your-secret-key",
    token_expiry_hours=24,
    enable_encryption=True
)
```

### Task Configuration
```python
task_manager = TaskManager(
    max_workers=4,
    queue_size=1000
)
```

## Extensibility

### Custom Tools
```python
def my_custom_function(param1, param2):
    # Your custom logic
    return {"result": "success"}

tool_manager.register_tool(
    name="my_tool",
    function=my_custom_function,
    description="My custom tool",
    parameters=[
        {"name": "param1", "type": "str", "required": True},
        {"name": "param2", "type": "int", "required": False}
    ],
    category="custom",
    tags=["custom", "automation"]
)
```

### Custom Modules
```python
def my_module_init(config):
    # Module initialization
    return True

def my_module_execute(*args, **kwargs):
    # Module execution
    return {"status": "success"}

def my_module_shutdown():
    # Module cleanup
    return True

module = module_manager.create_module(
    name="MyCustomModule",
    module_type=ModuleType.CUSTOM,
    initialize_func=my_module_init,
    execute_func=my_module_execute,
    shutdown_func=my_module_shutdown,
    category="custom",
    tags=["custom", "extension"]
)
```

## Roadmap

- [ ] API Layer (REST/GraphQL)
- [ ] Web Dashboard
- [ ] Advanced AI Integration (GPT, Claude, etc.)
- [ ] Real-time Collaboration
- [ ] Advanced Analytics Dashboard
- [ ] Multi-language Support
- [ ] Cloud Deployment Options
- [ ] Mobile App

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

**MutantSqr**

Built as part of an AI Software Engineering portfolio for business solutions and AI integration.