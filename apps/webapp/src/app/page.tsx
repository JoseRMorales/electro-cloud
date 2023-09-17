import SolarAnalysisApi from '@/lib/solarAnalysisApi'

const api = new SolarAnalysisApi()

const Home = async () => {
  const message = await api.getHelloSolar()
  return (
    <main>
      <h1>Hello World!</h1>
    </main>
  )
}

export default Home
