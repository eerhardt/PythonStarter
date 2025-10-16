import { useState, useEffect } from 'react'
import aspireLogo from '/Aspire.png'
import './App.css'

interface WeatherForecast {
  date: string
  temperatureC: number
  temperatureF: number
  summary: string
}

function App() {
  const [count, setCount] = useState(0)
  const [weatherData, setWeatherData] = useState<WeatherForecast[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchWeatherForecast = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await fetch('/api/weatherforecast')
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const data: WeatherForecast[] = await response.json()
      setWeatherData(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch weather data')
      console.error('Error fetching weather forecast:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchWeatherForecast()
  }, [])

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

      <div className="card">
        <h2>Weather Forecast</h2>
        <button onClick={fetchWeatherForecast} disabled={loading}>
          {loading ? 'Loading...' : 'Refresh Weather'}
        </button>
        
        {error && (
          <div style={{ color: 'red', margin: '10px 0' }}>
            Error: {error}
          </div>
        )}
        
        {weatherData.length > 0 && (
          <div className="weather-forecast">
            <table style={{ margin: '20px auto', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ backgroundColor: '#f0f0f0' }}>
                  <th style={{ padding: '10px', border: '1px solid #ccc' }}>Date</th>
                  <th style={{ padding: '10px', border: '1px solid #ccc' }}>Temperature (°C)</th>
                  <th style={{ padding: '10px', border: '1px solid #ccc' }}>Temperature (°F)</th>
                  <th style={{ padding: '10px', border: '1px solid #ccc' }}>Summary</th>
                </tr>
              </thead>
              <tbody>
                {weatherData.map((forecast, index) => (
                  <tr key={index}>
                    <td style={{ padding: '10px', border: '1px solid #ccc' }}>{forecast.date}</td>
                    <td style={{ padding: '10px', border: '1px solid #ccc', textAlign: 'center' }}>{forecast.temperatureC}°C</td>
                    <td style={{ padding: '10px', border: '1px solid #ccc', textAlign: 'center' }}>{forecast.temperatureF}°F</td>
                    <td style={{ padding: '10px', border: '1px solid #ccc' }}>{forecast.summary}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <p className="read-the-docs">
        Click on the Aspire logo to learn more
      </p>
    </>
  )
}

export default App
