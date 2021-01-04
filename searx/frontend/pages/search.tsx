import cx from 'classnames';
import { useRouter } from 'next/router';
import numeral from 'numeral';
import React from 'react';
import useSWR from 'swr';

import Navbar from '../components/Navbar';

const fetcher = async (_id, { q, category, format }: any) => {
  const res = await fetch(`http://localhost:8888/search`, {
    method: "POST",
    body: new URLSearchParams({
      q: q,
      format: format,
      [`category_${category}`]: "on",
      language: "en-US",
    }),
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
  });
  const data = await res.json();
  return data;
};

type Result = any;

type Infobox = any;

type Suggestion = any;

type SearchData = {
  query: string;
  number_of_results: number;
  results: Result[];
  answers: any;
  corrections: any;
  infoboxes: Infobox[];
  suggestions: Suggestion[];
  unresponsive_pages: any[];
};

const SkeletonResult = () => {
  return (
    <div className="flex">
      <div className="flex flex-col flex-1 min-w-0">
        <div className="h-4 mt-1 bg-gray-700 rounded" />

        <div className="mt-2 mb-1 space-y-1">
          <div className="h-4 pt-1">
            <div className="h-full bg-gray-700 rounded"></div>
          </div>
        </div>

        <div className="mt-1 mb-1 space-y-1">
          <div className="h-4 pt-1">
            <div className="h-full bg-gray-700 rounded"></div>
          </div>
          <div className="h-4 pt-1">
            <div className="h-full bg-gray-700 rounded"></div>
          </div>
          <div className="h-4 pt-1">
            <div className="h-full bg-gray-700 rounded"></div>
          </div>
        </div>
      </div>
    </div>
  );
};

const SkeletonInfo = () => (
  <div className="flex">
    <div className="flex flex-col flex-1 min-w-0">
      <div className="h-64 mt-1 bg-gray-700 rounded" />
    </div>
  </div>
);

const CATEGORIES = [
  {
    name: "general",
    Icon: () => (
      <svg
        className="w-5 h-5"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M8 16l2.879-2.879m0 0a3 3 0 104.243-4.242 3 3 0 00-4.243 4.242zM21 12a9 9 0 11-18 0 9 9 0 0118 0z"
        ></path>
      </svg>
    ),
  },
  {
    name: "files",
    Icon: () => (
      <svg
        className="w-5 h-5"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
        ></path>
      </svg>
    ),
  },
  {
    name: "images",
    Icon: () => (
      <svg
        className="w-5 h-5"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
        ></path>
      </svg>
    ),
  },
  {
    name: "it",
    Icon: () => (
      <svg
        className="w-5 h-5"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
        ></path>
      </svg>
    ),
  },
  {
    name: "map",
    Icon: () => (
      <svg
        className="w-5 h-5"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"
        ></path>
      </svg>
    ),
  },
  {
    name: "music",
    Icon: () => (
      <svg
        className="w-5 h-5"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3"
        ></path>
      </svg>
    ),
  },
  {
    name: "news",
    Icon: () => (
      <svg
        className="w-5 h-5"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z"
        ></path>
      </svg>
    ),
  },
  {
    name: "science",
    Icon: () => (
      <svg
        className="w-5 h-5"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"
        ></path>
      </svg>
    ),
  },
  {
    name: "social",
    Icon: () => (
      <svg
        className="w-5 h-5"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M17 8h2a2 2 0 012 2v6a2 2 0 01-2 2h-2v4l-4-4H9a1.994 1.994 0 01-1.414-.586m0 0L11 14h4a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2v4l.586-.586z"
        ></path>
      </svg>
    ),
  },
  {
    name: "videos",
    Icon: () => (
      <svg
        className="w-5 h-5"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"
        ></path>
      </svg>
    ),
  },
];

const SearchPage = () => {
  const { query, push } = useRouter();
  const [search, setSearch] = React.useState(() => {
    if (query && query.q && !Array.isArray(query.q)) {
      return query.q;
    }
    return "";
  });
  React.useEffect(() => {
    if (query && query.q) {
      setSearch(query.q);
    }
  }, [query]);
  const searchSWR = React.useMemo(() => {
    return query && query.q
      ? [
          `/search`,
          {
            q: query.q,
            category: query.category || "general",
            format: "json",
          },
        ]
      : null;
  }, [query]);
  const { data, error } = useSWR<SearchData>(searchSWR, fetcher);
  const handleSearchKeypress = (event) => {
    if (event.key == "Enter") {
      push(`/search?q=${search}`);
    }
  };
  const handleCateogryClick = (category) => {
    push(`/search?q=${search}&category=${category.name}`);
  };
  const handleSearchChange = (e) => {
    const value = e.currentTarget.value;
    if (value.split(" ")[0] === `!news` || value.startsWith(`!news`)) {
      const split = value.split(" ");
      split.shift();
      setSearch(split.join(" "));
      push(`/search?q=${split.join(" ")}&category=news`);
    }
    setSearch(value);
  };

  return (
    <div className="h-screen w-screen flex flex-col">
      <Navbar />
      <main className="w-screen flex justify-center">
        <div className="max-w-screen-lg w-full grid grid-cols-5 gap-4">
          <div className="flex col-span-5 px-2">
            <div className="flex items-center">
              {query && query.category && query.category !== "general" && (
                <div className="flex items-center justify-center bg-green-400 rounded-lg h-10 text-green-900 px-3 rounded-r-none">
                  {query.category}
                </div>
              )}
              <div className="relative text-gray-900">
                <input
                  type="text"
                  className={cx(
                    "h-10 w-96 pr-8 pl-3 rounded z-0 focus:shadow focus:outline-none",
                    {
                      "rounded-l-none":
                        query.category && query.category !== "general",
                    }
                  )}
                  placeholder="Search for..."
                  value={search}
                  onChange={handleSearchChange}
                  onKeyPress={handleSearchKeypress}
                />
                <div className="absolute top-3 right-3">
                  <svg
                    className="w-4 h-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                    ></path>
                  </svg>
                </div>
              </div>
            </div>
          </div>
          <div className="flex space-x-3 col-span-5 px-2">
            {CATEGORIES.map((category) => (
              <button
                onClick={() => handleCateogryClick(category)}
                className={cx("", {
                  "text-green-400": query.category
                    ? category.name === query.category
                    : category.name === "general",
                })}
              >
                <div className="flex items-center space-x-1">
                  {<category.Icon />}
                  <span>{category.name}</span>
                </div>
              </button>
            ))}
          </div>
          {error && (
            <div className="px-2 col-span-5">
              <div
                className="bg-red-800 text-red-300 px-4 py-3 rounded relative"
                role="alert"
              >
                <strong className="font-bold mr-3">Error: </strong>
                <span className="block sm:inline">{error.toString()}</span>
              </div>
            </div>
          )}
          {!data && (
            <>
              <div className="col-span-3 px-2">
                {[...new Array(10)].map((n, i) => (
                  <div
                    className="py-2"
                    style={{
                      animationFillMode: "backwards",
                      animationDelay: `${150 * i}ms`,
                    }}
                  >
                    <div className="animate-pulse">
                      <SkeletonResult />
                    </div>
                  </div>
                ))}
              </div>
              {!query.category ||
                (query.category === "general" && (
                  <div className="col-span-2">
                    <div className="animate-pulse">
                      <SkeletonInfo />
                    </div>
                  </div>
                ))}
            </>
          )}
          {data && !error && (
            <>
              <div className="col-span-3">
                <div className="mb-3 px-2">
                  <p className="text-sm text-gray-400">
                    About {numeral(data.number_of_results).format("0,0")}
                    {` `}
                    results.
                  </p>
                </div>
                <div className="space-y-2">
                  {data.results.map((result) => (
                    <div
                      key={result.url}
                      className="p-2 cursor-pointer rounded-md border border-gray-900 hover:border-gray-300"
                    >
                      <div className="flex justify-between">
                        <div>
                          <h2 className="text-lg hover:underline">
                            {result.title}
                          </h2>
                          <p className="text-sm text-green-500 hover:underline">
                            {result.url}
                          </p>
                        </div>
                        <div className="space-x-2">
                          {result.engines.map((engine) => (
                            <span className="py-1 px-2 font-bold text-sm bg-gray-300 text-gray-600 rounded-md">
                              {engine}
                            </span>
                          ))}
                        </div>
                      </div>
                      <p>{result.content}</p>
                    </div>
                  ))}
                </div>
              </div>
              <div className="col-span-2">
                <div className="mb-3">
                  {data.infoboxes.map((infobox) => (
                    <div className="border border-gray-300 p-2 rounded-md bg-gray-800">
                      <div className="flex justify-between mb-2">
                        <h1 className="text-2xl font-bold">
                          {infobox.infobox}
                        </h1>
                        <div className="space-x-2">
                          {infobox.engines.map((engine) => (
                            <span className="py-1 px-2 font-bold text-sm bg-gray-300 text-gray-600 rounded-md">
                              {engine}
                            </span>
                          ))}
                        </div>
                      </div>
                      <p className="text-sm">{infobox.content}</p>
                      <ul className="text-sm my-3">
                        {infobox.attributes &&
                          infobox.attributes.map((attribute) => (
                            <li>
                              <span className="font-bold mr-2">
                                {attribute.label}:
                              </span>
                              <span>{attribute.value}</span>
                            </li>
                          ))}
                      </ul>
                    </div>
                  ))}
                </div>
                {data.suggestions && data.suggestions.length > 0 && (
                  <div className="border border-gray-300 p-2 rounded-md bg-gray-800">
                    <h2 className="font-bold mb-2">Search suggestions</h2>
                    <ul>
                      {data.suggestions.map((suggestion) => (
                        <li>{suggestion}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      </main>
    </div>
  );
};

// export async function getStaticProps(context) {
//   console.log("context", context);
//   const res = await fetch(
//     `http://localhost:8888/search?q=${context.params.query}&format=json`
//   );
//   const data = await res.json();

//   if (!data) {
//     return {
//       notFound: true,
//     };
//   }

//   return {
//     props: data,
//   };
// }

// export async function getStaticPaths() {
//   return { paths: [], fallback: true };
// }

export default SearchPage;
