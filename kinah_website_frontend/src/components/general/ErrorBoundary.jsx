import { useRouteError } from "react-router-dom";

export default function ErrorBoundary() {
  const error = useRouteError();

  console.error(error);

  return (
    <div>
      <h1>Something went wrong</h1>
      <p>{error.statusText || error.message}</p>
    </div>
  );
}