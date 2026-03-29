import { createBrowserRouter, useLoaderData, } from "react-router";
import { useParams } from "react-router";
import AppLayout from "../components/layouts/AppLayout";
import HomePage from "../pages/HomePage";
import LandingPage from "../pages/LandingPage";
import ProductPage from "../pages/ProductPage";
import OrderPage from "../pages/OrderPage";
import CartPage from "../pages/CartPage";
import CheckoutPage from "../pages/CheckoutPage";
import UserProfilePage from "../pages/UserProfilePage";


export const router = createBrowserRouter([
  {
    path: "/",
    element: <AppLayout />,
    children: [
      { index: true, element: <HomePage />},
      { path: "landing-page", element: <LandingPage /> },
      { path: "products/:id", element: <ProductPage /> },
      { path: "orders", element: <OrderPage /> },
      { path: "cart", element: <CartPage /> },
      { path: "checkout", element: <CheckoutPage /> },
      { path: "me", element: <UserProfilePage /> },
      // {
      //   path: "auth",
      //   loader: () => {
      //     loggingMiddleware()
      //     console.log("Auth route hit");
      //     return null;
      //   },
      //   element: <AuthLayout />,
      //   children: [
      //     { path: "login", element: Login },
      //     { path: "register", element: Register },
      //   ],
      // },
    //   {
    //     path: "landing-page",
    //     children: [
    //       { index: true, Component: ConcertsHome },
    //       { path: ":city", Component: ConcertsCity },
    //       { path: "trending", Component: ConcertsTrending },
    //     ],
    //   },
    //   {
    //     path: "/teams/:teamId",
    //     loader: async ({ params }) => {
    //         // params are available in loaders/actions
    //         let team = await fetchTeam(params.teamId);
    //         return { name: team.name };
    //     },
    //     Component: Team,
    // },
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