# TripSmith - AI Travel Assistant

A conversation-first travel planning assistant that demonstrates advanced prompt engineering and natural LLM interactions. Built with local LLM inference and external API integration for reliable, context-aware travel recommendations.

## Overview

TripSmith is designed to showcase sophisticated conversation management, tool integration, and prompt engineering techniques. The system prioritizes conversation quality and factual accuracy over speed, using local LLM processing to ensure reliable, hallucination-resistant responses.

## Key Features

### Conversational Intelligence
- **Context-Aware Responses**: Builds upon previous exchanges rather than starting fresh
- **Anti-Repetition Logic**: Detects when users add constraints and refines suggestions accordingly
- **Progressive Planning**: Escalates from general recommendations to specific logistics
- **Natural Tool Integration**: Incorporates external data seamlessly without exposing technical details

### Travel Planning Capabilities
- **Smart Destination Recommendations**: Considers season, weather, crowds, and budget constraints
- **Budget-Conscious Planning**: Regional cost modeling with flight estimates from Tel Aviv
- **Personalized Guidance**: Adapts suggestions for solo travelers, families, and couples
- **Event Discovery**: Live event information via external APIs
- **Weather Intelligence**: Climate data integration for seasonal planning

### Technical Architecture
- **Multi-Stage Prompt Pipeline**: Modular prompt system with specialized components
- **Reliable Tool Integration**: Weather data, event discovery, and budget calculations
- **Error-Resilient Design**: Graceful handling of API failures and missing data
- **Local LLM Processing**: Privacy-focused inference with Ollama

## Installation

### Prerequisites
- Python 3.8+
- Ollama installed and running
- Virtual environment (recommended)

### Setup
1. **Clone the repository**
   ```bash
   git clone https://github.com/roetnoa1/TravelAssistant.git
   cd TravelAssistant
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Ollama**
   ```bash
   # Start Ollama service
   ollama serve
   
   # In another terminal, pull the model
   ollama pull llama3
   ```

5. **Optional: Configure external APIs**
   ```bash
   # Create .env file for optional API keys
   echo "TICKETMASTER_API_KEY=your_api_key_here" > .env
   ```

6. **Run the assistant**
   ```bash
   python main.py
   ```

## Usage Examples

### Budget Planning
```
You: I have $800 total from Tel Aviv for a 4-day trip in November - where can I go?

TripSmith: Smart Travel Recommendations
• Budapest, Hungary: thermal baths, stunning architecture ($830 estimated total)
• Prague, Czech Republic: charming streets, vibrant culture ($780 estimated total)
• Vienna, Austria: grand palaces, Christmas markets ($850 estimated total)

Budget Breakdown:
• $350 on flights from Tel Aviv
• $120 per day for accommodations, food, activities

Want me to help you plan a daily itinerary in one of these destinations?
```

### Context-Aware Refinement
```
You: I want somewhere warm in September that's not crowded

TripSmith: [provides general recommendations]

You: I'm a solo traveler into photography and food scenes

TripSmith: Foodie Photography Escapes
• Porto, Portugal: Mercado do Bolhão marketplace, vibrant street life
• Specific photography spots in historic neighborhoods
• Solo-friendly local food experiences

Want me to suggest specific photography spots or foodie tours?
```

## Architecture

### Core Components
- **`main.py`**: Orchestrates conversation flow with context management
- **`prompts.py`**: Multi-layered prompt engineering system
- **`llm.py`**: Local LLM integration via Ollama
- **`tools/`**: External API integrations (weather, events, budget)
- **`utils/`**: Date normalization and entity processing

### Conversation Flow
```
User Input → Intent Classification → Context Analysis → Tool Selection → Response Generation → Context Update
```

### Prompt Engineering Pipeline
1. **System Prompt**: Establishes personality and interaction patterns
2. **Router Prompt**: Few-shot intent classification and entity extraction
3. **Context Prompts**: Dynamic context-aware response guidance
4. **Tool Prompts**: Hidden data integration instructions
5. **Validation Prompts**: Self-checking and error prevention

## API Integrations

### Weather Data
- **Meteostat**: Historical climate normals
- **Open-Meteo**: Geocoding for location resolution
- Provides seasonal temperature and precipitation data

### Events Discovery
- **Ticketmaster API**: Live event information (optional)
- Graceful degradation when API unavailable
- Regional event discovery with temporal filtering

### Budget Intelligence
- Regional cost modeling with Israeli traveler focus
- Flight cost estimates from Tel Aviv
- Accommodation and activity cost breakdowns

## Design Decisions

### LLM Selection
The system was developed and tested with multiple LLM providers (Groq, local Ollama). Ollama was chosen for production use due to:
- Lower hallucination rates compared to faster cloud providers
- Privacy-focused local processing
- Reliable, conservative response generation
- No rate limits or API costs

### Conversation Management
- **Anti-repetition**: Distinguishes between user refinement requests and system repetition
- **Context building**: Maintains conversation state across multiple exchanges
- **Progressive detail**: Escalates from overview to specific planning naturally

### Error Handling Philosophy
- **Transparent limitations**: Acknowledges when data is unavailable rather than fabricating
- **Graceful degradation**: Continues conversation flow despite tool failures
- **User-centric recovery**: Offers alternative approaches when primary data sources fail

## File Structure
```
TravelAssistant/
├── main.py                 # Main conversation orchestrator
├── llm.py                  # Ollama integration
├── prompts.py              # Prompt engineering system
├── requirements.txt        # Python dependencies
├── conversation_logs.txt   # Sample conversations
├── tools/
│   ├── budget.py          # Regional cost modeling
│   ├── weather.py         # Climate data integration
│   ├── events.py          # Event discovery
│   └── formatter.py       # Data formatting utilities
└── utils/
    └── date_utils.py      # Date normalization helpers
```

## Configuration

### Environment Variables
- `TICKETMASTER_API_KEY`: Optional event discovery (system works without)
- Additional API keys can be added to `.env` file

### Model Configuration
- Default: `llama3` via Ollama
- Configurable in `llm.py` chat function
- Supports other Ollama-compatible models

## Limitations and Future Enhancements

### Current Limitations
- Weather data limited to climate normals (not real-time forecasts)
- Event discovery depends on external API availability
- Budget estimates are regional averages, not real-time pricing

### Potential Improvements
- Real-time flight price integration
- More sophisticated conversation memory compression
- Multi-language support for international travelers
- Integration with booking platforms

## Development Notes

This project demonstrates prompt engineering techniques for building reliable, conversational AI systems. The focus is on conversation quality, factual accuracy, and user experience rather than raw performance metrics.

Key technical achievements:
- Sophisticated anti-repetition detection
- Multi-modal tool integration with graceful failure handling
- Context-aware conversation management
- Regional intelligence for specific user demographics

## Contributing

This project was developed as a demonstration of conversation-first LLM engineering. The codebase prioritizes clarity and educational value over production optimization.

## License

[Add your chosen license here]
