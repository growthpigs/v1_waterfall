import React from "react";
import { createBrowserRouter, RouterProvider } from "react-router-dom";

export function createTestRouter(element: React.ReactElement) {
  const router = createBrowserRouter(
    [
      {
        path: "*",
        element: element,
      },
    ],
    {
      future: {
        // Enable React Router v7 future flags one at a time for smooth migration
        // Currently enabling the most stable flag first
        v7_startTransition: true,
        // TODO: Enable these flags one by one after testing each change:
        // v7_relativeSplatPath: true,
        // v7_fetcherPersist: true,
        // v7_normalizeFormMethod: true,
        // v7_partialHydration: true,
        // v7_skipActionErrorRevalidation: true,
      },
    }
  );

  return <RouterProvider router={router} />;
}

export function TestRouterWrapper({ children }: { children: React.ReactNode }) {
  return createTestRouter(<>{children}</>);
}