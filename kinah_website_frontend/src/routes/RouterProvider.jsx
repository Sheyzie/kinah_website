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
import { productLoader } from "../loaders/productLoader";
import AuthLayout from "../components/layouts/AuthLayout";
import LoginPage from "../pages/LoginPage";
import ErrorBoundary from "../components/general/ErrorBoundary";
import RegisterPage from "../pages/RegisterPage";
import ForgotPassword from "../pages/ForgetPassword";
import PasswordResetPage from "../pages/PasswordResetPage";


export const router = createBrowserRouter([
  {
    path: "/",
    element: <AppLayout />,
    errorElement: <ErrorBoundary />,
    children: [
      { index: true, element: <HomePage />},
      { path: "landing-page", element: <LandingPage /> },
      { path: "products/:id", element: <ProductPage />, loader: productLoader },
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
      //     { path: "login", element: <LoginPage /> },
      //     // { path: "register", element: Register },
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
  {
    path: "auth",
    loader: withLogging(async () => {
      console.log("Auth route hit");
      return null;
    }),
    element: <AuthLayout />,
    errorElement: <ErrorBoundary />,
    children: [
      { path: "login", element: <LoginPage /> },
      { path: "register", element: <RegisterPage /> },
      { path: "forget-password", element: <ForgotPassword /> },
    ],
  },
  { path: "accounts/set-password/:uid/:token/", 
    element: <AuthLayout />,
    errorElement: <ErrorBoundary />,
    children: [
      {index: true, element: <PasswordResetPage />},
    ]
  },
]);

function Team() {
  let data = useLoaderData();

  // params are available in components through useParams
  let params = useParams();

  return <h1>{data.name}</h1>;
}

function withLogging(loaderFn) {
  return async (args) => {
    const url = new URL(args.request.url);
    console.log(`Starting navigation: ${url.pathname}${url.search}`);

    const start = performance.now();

    try {
      const result = await loaderFn(args); // 👈 call actual loader
      return result;
    } finally {
      const duration = performance.now() - start;
      console.log(`Navigation completed in ${duration}ms`);
    }
  };
}

// const userContext = createContext<User>();
async function authMiddleware ({ context }) {
  const userId = getUserId();

  if (!userId) {
    throw redirect("/login");
  }

  context.set(userContext, await getUserById(userId));
};