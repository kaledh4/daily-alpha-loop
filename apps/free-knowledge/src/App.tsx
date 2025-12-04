import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [news, setNews] = useState<any>(null)
  const [crypto, setCrypto] = useState<any>(null)

  useEffect(() => {
    // In production (GitHub Pages), data is at ../../data/
    // Locally, we might need to mock it or copy it.
    const dataPath = import.meta.env.PROD ? '../../data' : '/data';

    fetch(`${dataPath}/news/latest.json`)
      .then(res => res.json())
      .then(data => setNews(data))
      .catch(err => console.error("Failed to fetch news", err))

    fetch(`${dataPath}/crypto/latest.json`)
      .then(res => res.json())
      .then(data => setCrypto(data))
      .catch(err => console.error("Failed to fetch crypto", err))
  }, [])

  return (
    <div className="container">
      <h1>Free Knowledge Dashboard</h1>
      <div className="grid">
        <div className="card">
          <h2>Latest News</h2>
          {news ? (
            <ul>
              {news.top_items.map((item: any, i: number) => (
                <li key={i}>
                  <a href={item.url} target="_blank" rel="noreferrer">{item.title}</a>
                  <p>{item.summary}</p>
                </li>
              ))}
            </ul>
          ) : (
            <p>Loading news... (Check console if failed)</p>
          )}
        </div>
        <div className="card">
          <h2>Crypto Market</h2>
          {crypto ? (
            <div>
              <p>BTC: ${crypto.numbers.btc_price?.toLocaleString()}</p>
              <p>ETH: ${crypto.numbers.eth_price?.toLocaleString()}</p>
            </div>
          ) : (
            <p>Loading crypto...</p>
          )}
        </div>
      </div>
    </div>
  )
}

export default App
