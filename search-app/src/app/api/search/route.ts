import { search } from "@/lib/db";

 
export async function GET(
  req: Request
) {
  try {
  const { searchParams } = new URL(req?.url);
  const searchQuery = searchParams.get('query');
  const index = searchParams.get('index');
  if (!index || !searchQuery || searchQuery.length < 3) {
    throw Error('Query is too short');
  }
  console.log('searching', {
    index,
    searchQuery,
  });
  const results = await search(index, searchQuery);
  console.log('search results', {
    results: results.length,
    index,
    searchQuery
  });
  return new Response(JSON.stringify(results), {
    status: 200,
  });
} catch (error) {
  console.error('error in querying', error);
  return new Response(JSON.stringify({ message: "Something went wrong" }), {
    status: 500,
  });
}
}

