import { Client } from '@elastic/elasticsearch';

const SEARCH_LOGS_INDEX = 'search_logs';
const HOST = process.env.ELASTICSEARCH_HOST || 'localhost';
const PORT = process.env.ELASTICSEARCH_PORT || '9200';
const USER_NAME = process.env.ELASTICSEARCH_USERNAME || 'elastic'
const PASSWORD = process.env.ELASTICSEARCH_PASSWORD || 'changeme'
const client = new Client({
  node: `https://${HOST}:${PORT}`, auth: {
    username: USER_NAME,
    password: PASSWORD
  },
  ssl: {
    rejectUnauthorized: false,    // Disable certificate validation (useful for local dev)
  },
});

const getIndexMetaData = async ({ index, ...moreDetails }) => {
    const { body: result} = await client.search({
        index,
        body: {
            query: {
                match_all: {},
            },
            size: 1,
            sort: [
                {
                    'timestamp': 'desc',
                },
            ],
        },
    });
    return {
        index,
        documentsCount: moreDetails['docs.count'],
        lastUpdated: result?.hits?.hits[0]?._source['timestamp'],
    };
}

const getAvailableIndices = async () => {
  let { body: indices} = await client.cat.indices({ format: 'json' });
  indices = indices.filter(({ index }) => !index.startsWith('.') && index !== SEARCH_LOGS_INDEX);
  return indices;
}

export const getIndices = async () => {
    const availableIndices = await getAvailableIndices();
    const result = await Promise.all(availableIndices.map(getIndexMetaData));
    return result
}

export const search = async (index: string, query: string) => {
    const availableIndices = await getAvailableIndices();
    if (!availableIndices.find(({ index: idx }) => idx === index)) {
        throw new Error('Index not searchable');
    }
    const { body: result } = await client.search({
        index,
        body: {
            _source: ["file_path"],
        size: 10000,
        query: {
          bool: {
            should: [
              {
                match_phrase: {
                  text_heb: query
                }
              },
              {
                match_phrase: {
                  text_heb_eng: query
                }
              }
            ]
          }
        }
      }
    });
    return result?.hits?.hits.map((hit) => hit._source);
}

export const logSearchResult = async (index: string, query: string, resultsCount: number) => {
    await client.index({
        index: SEARCH_LOGS_INDEX,
        body: {
            indexName: index,
            searchQuery: query,
            results: resultsCount,
            timestamp: new Date().toISOString(),
        },
    });
}