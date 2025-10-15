import { useState } from 'react'
import aspireLogo from '/Aspire.png'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <div>
        <a href="https://aspire.dev" target="_blank">
          <img src={aspireLogo} className="logo" alt="Aspire logo" />
        </a>
      </div>
      <h1>Aspire Starter</h1>
      <div className="card">
        <button onClick={() => setCount((count) => count + 1)}>
          count is {count}
        </button>
      </div>
      <p className="read-the-docs">
        Click on the Aspire logo to learn more
      </p>
    </>
  )
}

export default App
