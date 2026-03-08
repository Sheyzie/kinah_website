import { createBrowserRouter, useLoaderData, } from "react-router";
import { RouterProvider } from "react-router/dom";
import { useParams } from "react-router";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: Root,
    children: [
      { index: true, Component: Home },
      { path: "about", Component: About },
      {
        path: "auth",
        middleware: [loggingMiddleware],
        Component: AuthLayout,
        children: [
          { path: "login", Component: Login },
          { path: "register", Component: Register },
        ],
      },
      {
        path: "concerts",
        children: [
          { index: true, Component: ConcertsHome },
          { path: ":city", Component: ConcertsCity },
          { path: "trending", Component: ConcertsTrending },
        ],
      },
      {
        path: "/teams/:teamId",
        loader: async ({ params }) => {
            // params are available in loaders/actions
            let team = await fetchTeam(params.teamId);
            return { name: team.name };
        },
        Component: Team,
    },
    ],
  },
]);

function Team() {
  let data = useLoaderData();

  // params are available in components through useParams
  let params = useParams();

  return <h1>{data.name}</h1>;
}

async function loggingMiddleware({ request }, next) {
  let url = new URL(request.url);
  console.log(`Starting navigation: ${url.pathname}${url.search}`);
  const start = performance.now();
  await next();
  const duration = performance.now() - start;
  console.log(`Navigation completed in ${duration}ms`);
}

// const userContext = createContext<User>();

async function authMiddleware ({ context }) {
  const userId = getUserId();

  if (!userId) {
    throw redirect("/login");
  }

  context.set(userContext, await getUserById(userId));
};