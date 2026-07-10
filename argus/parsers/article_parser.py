import trafilatura


def extract_article_text(url: str) -> str | None:
    downloaded = trafilatura.fetch_url(url)

    if downloaded is None:
        return None

    text = trafilatura.extract(downloaded)

    return text