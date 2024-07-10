from elasticsearch import AsyncElasticsearch

es: AsyncElasticsearch | None = None


async def get_elastic_instance() -> AsyncElasticsearch:
    return es
