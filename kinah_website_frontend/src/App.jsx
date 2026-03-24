import { useState } from 'react'
import { Refine } from "@refinedev/core";
import { dataProvider } from "./providers/dataProvider";
import { RouterProvider } from "react-router/dom";
import { router } from "./routes/RouterProvider"
import './App.css'


function App() {

  return (
    <>
      <Refine 
        dataProvider={dataProvider}
        routerProvider={router}
        >
        {/* Main Component */}
        <RouterProvider router={router} />
      </Refine>
    </>
  )
}

export default App
