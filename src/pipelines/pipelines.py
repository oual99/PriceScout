from src.agents.agents import (
    build_extracter_agent,
    build_researcher_agent,
    build_trust_scorer_agent,
    ranker_chain,
)


def run_price_scout_pipeline(product: str) -> dict:

    state = {}

    # step 1 - researcher agent
    print("\n" + "=" * 50)
    print("step 1 - researcher is searching for listings ...")
    print("=" * 50)

    researcher_agent = build_researcher_agent()
    researcher_result = researcher_agent.invoke({
        "messages": [("user", f"Find pages selling this product: {product}")]
    })
    state["urls"] = researcher_result["structured_response"].urls

    print("\nurls found:\n", state["urls"])

    # step 2 - extracter agent
    print("\n" + "=" * 50)
    print("step 2 - extracter is scraping listings ...")
    print("=" * 50)

    extracter_agent = build_extracter_agent()
    extracter_result = extracter_agent.invoke({
        "messages": [("user",
            f"Scrape and extract product info (price, stock, seller) for "
            f"'{product}' from these URLs:\n" + "\n".join(state["urls"])
        )]
    })
    state["listings"] = extracter_result["structured_response"].listings

    print("\nlistings extracted:\n", state["listings"])

    # step 3 - trust scorer agent
    print("\n" + "=" * 50)
    print("step 3 - trust scorer is checking seller reputations ...")
    print("=" * 50)

    sellers = sorted({listing.seller for listing in state["listings"]})

    trust_scorer_agent = build_trust_scorer_agent()
    trust_result = trust_scorer_agent.invoke({
        "messages": [("user",
            "Look up reviews/complaints and score the trustworthiness of these "
            "stores:\n" + "\n".join(sellers)
        )]
    })
    state["trust_scores"] = trust_result["structured_response"].scores

    print("\ntrust scores:\n", state["trust_scores"])

    # step 4 - ranker & formatter chain
    print("\n" + "=" * 50)
    print("step 4 - ranker is building the result table ...")
    print("=" * 50)

    listings_text = "\n".join(
        f"- {listing.seller}: {listing.price} (stock: {listing.stock}) - {listing.url}"
        for listing in state["listings"]
    )
    trust_scores_text = "\n".join(
        f"- {t.seller}: {t.score}/10 - {t.justification}"
        for t in state["trust_scores"]
    )

    state["result_table"] = ranker_chain.invoke({
        "listings": listings_text,
        "trust_scores": trust_scores_text,
    })

    print("\nresult table:\n", state["result_table"])

    return state
