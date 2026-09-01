from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel, Field
from src.tools.tools import web_search, scrape_url
from dotenv import load_dotenv

load_dotenv()

# Model Initialization
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


# Structured outputs
# Agents below use these as `response_format` so downstream pipeline steps get
# real data (urls, listings, scores) instead of having to parse free text.
class ResearchResult(BaseModel):
    urls: list[str] = Field(description="Relevant product listing URLs found")


class Listing(BaseModel):
    seller: str
    price: str
    stock: str
    url: str


class ExtractionResult(BaseModel):
    listings: list[Listing]


class TrustScore(BaseModel):
    seller: str
    score: float = Field(description="Trust score from 0 to 10")
    justification: str


class TrustScoringResult(BaseModel):
    scores: list[TrustScore]


# 1st Agent: Researcher
# Builds search queries for the product and uses the search tool (Tavily) to find candidate listings.
def build_researcher_agent():
    return create_agent(
        model=llm,
        tools=[web_search],
        system_prompt=(
            "You are a research agent for a price comparison tool focused on the "
            "Moroccan market. Given a product name, build effective search queries "
            "targeting Moroccan online stores (e.g. add terms like 'Maroc' or "
            "'prix' to the query, and prefer .ma domains or stores known to ship "
            "within Morocco) and use the search tool to find pages that sell this "
            "product. Include a price-related term (e.g. 'prix', 'price') in your "
            "queries to bias results toward pages that actually show a price."
        ),
        response_format=ResearchResult,
    )


# 2nd Agent: Extracter
# Scrapes the URLs found by the Researcher, combines the results, and extracts
# product info (price, stock, seller) from each page.
def build_extracter_agent():
    return create_agent(
        model=llm,
        tools=[scrape_url],
        system_prompt=(
            "You are an extraction agent for a price comparison tool. "
            "Given a list of URLs, use the scraping tool on each one, then combine "
            "all the results and extract structured product info: price, stock "
            "availability, and seller/store name for each listing."
        ),
        response_format=ExtractionResult,
    )


# 3rd Agent: Trust Scorer
# Uses Tavily to look for reviews and complaints about a given website (store)
# and produces a trust score.
def build_trust_scorer_agent():
    return create_agent(
        model=llm,
        tools=[web_search],
        system_prompt=(
            "You are a trust-scoring agent for a price comparison tool. "
            "Given a list of store/website names, use the search tool to look for "
            "reviews, complaints, and reputation signals about each one. "
            "Return a trust score from 0 to 10 with a short justification for each store."
        ),
        response_format=TrustScoringResult,
    )


# Ranker & Formatter chain
# Ranks the extracted listings based on trust score + pricing, then formats
# the final result table.
ranker_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a precise data formatter for a price comparison tool."),
    ("human", """Rank the product listings below using trust score and price
(lower price and higher trust score should rank higher).

Product listings (price, stock, seller):
{listings}

Trust scores per seller:
{trust_scores}

Return the result as a markdown table with columns:
Rank | Seller | Price | Stock | Trust Score | Trust Justification | URL"""),
])

ranker_chain = ranker_prompt | llm | StrOutputParser()
